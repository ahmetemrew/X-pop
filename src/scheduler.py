"""
Scheduler for running bot at intervals with human-like randomness
"""

import logging
import time
from datetime import datetime


class BotScheduler:
    def __init__(self, bot, interval_minutes: int = 5):
        """
        Initialize scheduler with smart interval support

        Args:
            bot: XPopBot instance
            interval_minutes: Base interval (in minutes)
        """
        self.bot = bot
        self.interval_minutes = interval_minutes
        self.logger = logging.getLogger(__name__)
        self.running = False

    def start(self):
        """Start the scheduler with dynamic intervals"""
        self.logger.info(f"⏰ Starting smart scheduler (base interval: {self.interval_minutes} minutes)")
        self.logger.info(f"🎲 Random timing enabled: {self.interval_minutes} + 5-20 minutes")

        self.running = True

        # Run immediately on start
        self.logger.info("🚀 Running initial cycle...")
        self._run_bot_cycle()

        # Start scheduler loop
        try:
            while self.running:
                # Get next interval with randomness
                random_config = self.bot.config.get('human_behavior', {}).get('random_timing', {})

                if random_config.get('enabled', True):
                    min_extra = random_config.get('min_extra_minutes', 5)
                    max_extra = random_config.get('max_extra_minutes', 20)
                    next_interval = self.bot.smart_scheduler.get_next_interval(min_extra, max_extra)
                else:
                    next_interval = self.interval_minutes

                # Calculate wait time
                wait_seconds, formatted_time = self.bot.smart_scheduler.calculate_wait_time(next_interval)

                self.logger.info(f"⏰ Next check in: {formatted_time}")
                self.logger.info(f"📅 Next run at: {self._format_next_run_time(wait_seconds)}")

                # Sleep until next cycle
                time.sleep(wait_seconds)

                # Check if still running (could be stopped during sleep)
                if self.running:
                    self._run_bot_cycle()

        except KeyboardInterrupt:
            self.logger.info("⏹️  Scheduler stopped by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}", exc_info=True)
            self.stop()

    def _run_bot_cycle(self):
        """Wrapper for running bot cycle with error handling and working hours check"""
        try:
            # Check working hours
            if not self.bot.human_behavior.is_working_hours():
                self.logger.info("😴 Outside working hours, skipping this cycle")
                # Bot will wait until next scheduled run
                return

            self.bot.run_cycle()

        except Exception as e:
            self.logger.error(f"Error in scheduled bot cycle: {e}", exc_info=True)

    def _format_next_run_time(self, seconds: int) -> str:
        """Format next run time"""
        from datetime import datetime, timedelta
        next_time = datetime.now() + timedelta(seconds=seconds)
        return next_time.strftime('%Y-%m-%d %H:%M:%S')

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.logger.info("Scheduler stopped")
