"""
Scheduler for running bot at intervals with human-like randomness - CRASH-PROOF
"""

import logging
import time
from datetime import datetime, timedelta


class BotScheduler:
    def __init__(self, bot, interval_minutes: int = 5):
        """
        Initialize scheduler with smart interval support - CRASH-PROOF

        Args:
            bot: XPopBot instance
            interval_minutes: Base interval (in minutes)
        """
        self.bot = bot
        self.interval_minutes = interval_minutes
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.cycle_count = 0
        self.error_count = 0

    def start(self):
        """Start the scheduler with dynamic intervals - CRASH-PROOF"""
        self.logger.info(f"⏰ Starting smart scheduler (base interval: {self.interval_minutes} minutes)")
        self.logger.info(f"🛡️  Crash-proof mode enabled")

        self.running = True

        # Run immediately on start
        self.logger.info("🚀 Running initial cycle...")
        self._run_bot_cycle()

        # Start scheduler loop - NEVER CRASHES
        try:
            while self.running:
                try:
                    # Get next interval with randomness - SAFE
                    next_interval = self._calculate_next_interval()

                    # Calculate wait time - SAFE
                    wait_seconds, formatted_time = self._calculate_wait_time(next_interval)

                    self.logger.info(f"⏰ Next check in: {formatted_time}")
                    self.logger.info(f"📅 Next run at: {self._format_next_run_time(wait_seconds)}")

                    # Sleep until next cycle
                    time.sleep(wait_seconds)

                    # Check if still running (could be stopped during sleep)
                    if self.running:
                        self._run_bot_cycle()

                except Exception as loop_error:
                    self.logger.error(f"⚠️  Error in scheduler loop: {loop_error}", exc_info=True)
                    self.logger.warning("🛡️  Continuing anyway (crash-proof mode)")
                    # Sleep a bit before retrying
                    time.sleep(60)
                    continue  # NEVER EXIT

        except KeyboardInterrupt:
            self.logger.info("⏹️  Scheduler stopped by user")
            self.stop()

    def _calculate_next_interval(self) -> int:
        """Calculate next interval with randomness - SAFE"""
        try:
            if not self.bot.config:
                return self.interval_minutes

            random_config = self.bot.config.get('human_behavior', {}).get('random_timing', {})

            if random_config.get('enabled', True):
                min_extra = random_config.get('min_extra_minutes', 5)
                max_extra = random_config.get('max_extra_minutes', 20)

                if self.bot.smart_scheduler:
                    return self.bot.smart_scheduler.get_next_interval(min_extra, max_extra)
                else:
                    # Fallback: simple random
                    import random
                    extra = random.randint(min_extra, max_extra)
                    return self.interval_minutes + extra
            else:
                return self.interval_minutes

        except Exception as e:
            self.logger.warning(f"⚠️  Error calculating interval: {e}, using default")
            return self.interval_minutes

    def _calculate_wait_time(self, interval_minutes: int) -> tuple:
        """Calculate wait time in seconds and formatted string - SAFE"""
        try:
            if self.bot.smart_scheduler:
                return self.bot.smart_scheduler.calculate_wait_time(interval_minutes)
            else:
                # Fallback: simple calculation
                wait_seconds = interval_minutes * 60
                formatted_time = f"{interval_minutes} minutes"
                return (wait_seconds, formatted_time)

        except Exception as e:
            self.logger.warning(f"⚠️  Error calculating wait time: {e}, using default")
            wait_seconds = self.interval_minutes * 60
            formatted_time = f"{self.interval_minutes} minutes"
            return (wait_seconds, formatted_time)

    def _run_bot_cycle(self):
        """Wrapper for running bot cycle with error handling and working hours check - CRASH-PROOF"""
        try:
            self.cycle_count += 1
            self.logger.info(f"🔄 Starting cycle #{self.cycle_count}")

            # Check working hours - SAFE
            try:
                if self.bot.human_behavior and hasattr(self.bot.human_behavior, 'is_working_hours'):
                    if not self.bot.human_behavior.is_working_hours():
                        self.logger.info("😴 Outside working hours, skipping this cycle")
                        return
            except Exception as wh_error:
                self.logger.warning(f"⚠️  Could not check working hours: {wh_error}")
                # Continue anyway

            # Run the bot cycle
            try:
                self.bot.run_cycle()
                self.logger.info(f"✅ Cycle #{self.cycle_count} completed successfully")
            except Exception as cycle_error:
                self.error_count += 1
                self.logger.error(f"❌ Error in cycle #{self.cycle_count}: {cycle_error}", exc_info=True)
                self.logger.warning(f"🛡️  Error count: {self.error_count} (bot will continue)")

        except Exception as e:
            self.error_count += 1
            self.logger.error(f"❌ Error in scheduled bot cycle: {e}", exc_info=True)
            self.logger.warning(f"🛡️  Error count: {self.error_count} (bot will continue)")

    def _format_next_run_time(self, seconds: int) -> str:
        """Format next run time"""
        try:
            next_time = datetime.now() + timedelta(seconds=seconds)
            return next_time.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return "unknown"

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.logger.info(f"⏹️  Scheduler stopped (ran {self.cycle_count} cycles, {self.error_count} errors)")
