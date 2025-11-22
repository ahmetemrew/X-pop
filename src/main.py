"""
Main entry point for X-Pop Bot - BULLETPROOF VERSION
This entry point NEVER crashes. It retries indefinitely.
"""

import sys
import argparse
import os
import time
import traceback
from colorama import init, Fore, Style

# Initialize colorama
init()

from .bot import XPopBot
from .scheduler import BotScheduler


def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════╗
║                                                   ║
║              {Fore.YELLOW}🤖  X-POP BOT  🤖{Fore.CYAN}                  ║
║                                                   ║
║     {Fore.WHITE}Twitter/X AI Bot with Personality{Fore.CYAN}          ║
║         {Fore.GREEN}🛡️  BULLETPROOF MODE 🛡️{Fore.CYAN}               ║
║                                                   ║
╚═══════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print(f"{Fore.RED}❌ .env file not found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please copy .env.example to .env and fill in your API keys{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Steps:")
        print(f"  1. cp .env.example .env")
        print(f"  2. Edit .env and add your API keys")
        print(f"  3. Run the bot again{Style.RESET_ALL}\n")
        return False
    return True


def main():
    """Main function - BULLETPROOF with infinite retry"""
    print_banner()

    parser = argparse.ArgumentParser(description='X-Pop Bot - AI-powered Twitter/X bot')
    parser.add_argument('--test', action='store_true', help='Test API connections')
    parser.add_argument('--dry-run', action='store_true', help='Run without posting tweets')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=5, help='Interval in minutes (default: 5)')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Config file path')

    args = parser.parse_args()

    # Check .env file
    if not check_env_file():
        print(f"{Fore.RED}⚠️  .env file missing but bot will retry...{Style.RESET_ALL}")
        # Don't exit - will retry

    # BULLETPROOF MODE: Infinite retry loop
    retry_count = 0
    max_retry_delay = 300  # Max 5 minutes between retries

    while True:  # NEVER EXIT
        try:
            retry_count += 1

            # Initialize bot
            print(f"{Fore.CYAN}Initializing bot (attempt #{retry_count})...{Style.RESET_ALL}")
            bot = None

            try:
                bot = XPopBot(config_path=args.config)
            except Exception as init_error:
                print(f"{Fore.RED}❌ Bot initialization failed: {init_error}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}⏳ Retrying in 30 seconds...{Style.RESET_ALL}")
                time.sleep(30)
                continue  # Retry initialization

            # Test mode
            if args.test:
                print(f"\n{Fore.YELLOW}🧪 Testing API connections...{Style.RESET_ALL}\n")
                try:
                    if bot.test_connection():
                        print(f"\n{Fore.GREEN}✅ All connections successful!{Style.RESET_ALL}\n")
                    else:
                        print(f"\n{Fore.RED}❌ Connection test failed{Style.RESET_ALL}\n")
                except Exception as test_error:
                    print(f"\n{Fore.RED}❌ Test error: {test_error}{Style.RESET_ALL}\n")
                return  # Exit on test mode

            # Dry run mode
            if args.dry_run:
                print(f"\n{Fore.YELLOW}🧪 Running in DRY RUN mode...{Style.RESET_ALL}\n")
                try:
                    bot.dry_run()
                except Exception as dry_run_error:
                    print(f"\n{Fore.RED}❌ Dry run error: {dry_run_error}{Style.RESET_ALL}\n")
                    traceback.print_exc()
                return  # Exit on dry-run mode

            # Run once mode
            if args.once:
                print(f"\n{Fore.CYAN}▶️  Running one cycle...{Style.RESET_ALL}\n")
                try:
                    bot.run_cycle()
                    print(f"\n{Fore.GREEN}✅ Cycle completed{Style.RESET_ALL}\n")
                except Exception as cycle_error:
                    print(f"\n{Fore.RED}❌ Cycle error: {cycle_error}{Style.RESET_ALL}\n")
                    traceback.print_exc()
                return  # Exit on once mode

            # Continuous mode with scheduler
            print(f"\n{Fore.GREEN}✅ Bot initialized successfully{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🛡️  BULLETPROOF MODE: Bot will auto-recover from any error{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Starting scheduler (every {args.interval} minutes)...{Style.RESET_ALL}\n")

            try:
                scheduler = BotScheduler(bot, interval_minutes=args.interval)
                scheduler.start()
            except Exception as scheduler_error:
                print(f"{Fore.RED}❌ Scheduler crashed: {scheduler_error}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}📊 Stack trace:{Style.RESET_ALL}")
                traceback.print_exc()

                # Calculate exponential backoff
                retry_delay = min(30 * (2 ** min(retry_count - 1, 3)), max_retry_delay)
                print(f"{Fore.YELLOW}⏳ Restarting in {retry_delay} seconds...{Style.RESET_ALL}")
                time.sleep(retry_delay)
                continue  # Restart the whole bot

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Bot stopped by user{Style.RESET_ALL}\n")
            try:
                if bot:
                    bot.cleanup()
            except:
                pass
            sys.exit(0)  # Only exit on user request

        except Exception as fatal_error:
            print(f"\n{Fore.RED}❌ Unexpected error: {fatal_error}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}📊 Stack trace:{Style.RESET_ALL}")
            traceback.print_exc()

            # Calculate exponential backoff
            retry_delay = min(30 * (2 ** min(retry_count - 1, 3)), max_retry_delay)
            print(f"{Fore.YELLOW}🛡️  BULLETPROOF MODE: Restarting in {retry_delay} seconds...{Style.RESET_ALL}")
            time.sleep(retry_delay)
            continue  # NEVER EXIT, always retry


if __name__ == '__main__':
    main()
