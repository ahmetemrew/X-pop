"""
Scheduler for running bot at intervals
"""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime


class BotScheduler:
    def __init__(self, bot, interval_minutes: int = 5):
        """
        Initialize scheduler

        Args:
            bot: XPopBot instance
            interval_minutes: How often to run (in minutes)
        """
        self.bot = bot
        self.interval_minutes = interval_minutes
        self.scheduler = BlockingScheduler()
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start the scheduler"""
        self.logger.info(f"⏰ Starting scheduler (interval: {self.interval_minutes} minutes)")

        # Add job to run at intervals
        self.scheduler.add_job(
            func=self._run_bot_cycle,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id='bot_cycle',
            name='Run bot cycle',
            replace_existing=True
        )

        # Run immediately on start
        self.logger.info("🚀 Running initial cycle...")
        self._run_bot_cycle()

        # Start scheduler
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("⏹️  Scheduler stopped by user")
            self.scheduler.shutdown()

    def _run_bot_cycle(self):
        """Wrapper for running bot cycle with error handling"""
        try:
            self.bot.run_cycle()
        except Exception as e:
            self.logger.error(f"Error in scheduled bot cycle: {e}", exc_info=True)

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")
