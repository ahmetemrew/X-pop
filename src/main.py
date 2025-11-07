"""
Main entry point for X-Pop Bot
"""

import sys
import argparse
import os
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
    """Main function"""
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
        sys.exit(1)

    try:
        # Initialize bot
        print(f"{Fore.CYAN}Initializing bot...{Style.RESET_ALL}")
        bot = XPopBot(config_path=args.config)

        # Test mode
        if args.test:
            print(f"\n{Fore.YELLOW}🧪 Testing API connections...{Style.RESET_ALL}\n")
            if bot.test_connection():
                print(f"\n{Fore.GREEN}✅ All connections successful!{Style.RESET_ALL}\n")
            else:
                print(f"\n{Fore.RED}❌ Connection test failed{Style.RESET_ALL}\n")
            return

        # Dry run mode
        if args.dry_run:
            print(f"\n{Fore.YELLOW}🧪 Running in DRY RUN mode...{Style.RESET_ALL}\n")
            bot.dry_run()
            return

        # Run once mode
        if args.once:
            print(f"\n{Fore.CYAN}▶️  Running one cycle...{Style.RESET_ALL}\n")
            bot.run_cycle()
            print(f"\n{Fore.GREEN}✅ Cycle completed{Style.RESET_ALL}\n")
            return

        # Continuous mode with scheduler
        print(f"\n{Fore.GREEN}✅ Bot initialized successfully{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Starting scheduler (every {args.interval} minutes)...{Style.RESET_ALL}\n")

        scheduler = BotScheduler(bot, interval_minutes=args.interval)
        scheduler.start()

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Bot stopped by user{Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
