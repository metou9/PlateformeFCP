import json
import logging
import time
from datetime import timedelta
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from formulaire.views import _impression_job_dir, _ecrire_job, _traiter_impression_pdf

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Traite les demandes PDF hors des requêtes HTTP.'

    def handle(self, *args, **options):
        directory = _impression_job_dir()
        self.stdout.write('Worker PDF démarré')
        while True:
            for path in sorted(directory.glob('*.json')):
                try:
                    job_id = path.stem
                    job = json.loads(path.read_text(encoding='utf-8'))
                    if job.get('state') != 'pending':
                        continue
                    # Claim atomique ; un seul worker peut traiter la demande.
                    claim = directory / (job_id + '.lock')
                    try:
                        with claim.open('x'):
                            pass
                    except FileExistsError:
                        continue
                    try:
                        job = json.loads(path.read_text(encoding='utf-8'))
                        if job.get('state') != 'pending':
                            continue
                        job['state'] = 'running'
                        _ecrire_job(job_id, job)
                        try:
                            _traiter_impression_pdf(job_id, job)
                            job['state'] = 'ready'
                        except Exception:
                            logger.exception('Erreur impression PDF %s', job_id)
                            job['state'] = 'error'
                            job['error'] = 'Échec de génération (voir logs worker).'
                        _ecrire_job(job_id, job)
                    finally:
                        claim.unlink(missing_ok=True)
                except Exception:
                    logger.exception('Erreur de lecture d’une demande PDF')
            time.sleep(3)
