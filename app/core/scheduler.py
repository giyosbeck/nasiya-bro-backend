from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.magazine_service import check_and_deactivate_expired_magazines
from app.services.subscription_service import check_and_deactivate_expired_users
import logging

logger = logging.getLogger(__name__)

class AppScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Background scheduler started")
    
    def start_daily_checks(self):
        """Start daily expiration checks for both users and magazines"""
        
        # Daily magazine expiration check at 2:00 AM
        self.scheduler.add_job(
            func=self._daily_magazine_check,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_magazine_check",
            name="Daily Magazine Expiration Check",
            replace_existing=True
        )
        
        # Daily user expiration check at 2:30 AM
        self.scheduler.add_job(
            func=self._daily_user_check,
            trigger=CronTrigger(hour=2, minute=30),
            id="daily_user_check",
            name="Daily User Expiration Check",
            replace_existing=True
        )
        
        logger.info("Daily expiration checks scheduled")
    
    def _daily_magazine_check(self):
        """Wrapper for magazine expiration check with logging"""
        try:
            logger.info("Starting daily magazine expiration check")
            result = check_and_deactivate_expired_magazines()
            logger.info(f"Daily magazine check completed: {result['message']}")
            
            if result['total_deactivated'] > 0:
                logger.warning(f"Deactivated {result['total_deactivated']} expired magazines")
                
        except Exception as e:
            logger.error(f"Error in daily magazine check: {str(e)}")
    
    def _daily_user_check(self):
        """Wrapper for user expiration check with logging"""
        try:
            logger.info("Starting daily user expiration check")
            result = check_and_deactivate_expired_users()
            logger.info(f"Daily user check completed: {result['message']}")
            
            if result['total_deactivated'] > 0:
                logger.warning(f"Deactivated {result['total_deactivated']} expired users")
                
        except Exception as e:
            logger.error(f"Error in daily user check: {str(e)}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Background scheduler stopped")
    
    def get_jobs(self):
        """Get information about scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs

# Global scheduler instance
app_scheduler = AppScheduler()