# risk_calculator/cli.py

from risk_calculator.portfolio import Portfolio, Position


def print_help() -> None:
    print("""
Commands:
  add SYMBOL QUANTITY PRICE   Add (or merge) a position
  update SYMBOL PRICE         Update price of existing position
  remove SYMBOL               Remove a position
  show                        Show current portfolio
  help                        Show this help
  quit                        Exit
""")


def main() -> None:
    portfolio = Portfolio()
    print("Simple Portfolio Calculator")
    print_help()

    while True:
        try:
            raw = input("> ").strip()
        except EOFError, KeyboardInterrupt:
            print("\nBye")
            break

        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()

        try:
            if command == "quit":
                print("Bye")
                break

            elif command == "help":
                print_help()

            elif command == "show":
                print(portfolio)
                print()

            elif command == "add":
                if len(parts) != 4:
                    print("Usage: add SYMBOL QUANTITY PRICE")
                    continue
                _, symbol, qty, price = parts
                portfolio.add_position(Position(symbol, float(qty), float(price)))
                print("OK")

            elif command == "update":
                if len(parts) != 3:
                    print("Usage: update SYMBOL PRICE")
                    continue
                _, symbol, price = parts
                portfolio.update_price(symbol, float(price))
                print("OK")

            elif command == "remove":
                if len(parts) != 2:
                    print("Usage: remove SYMBOL")
                    continue
                portfolio.remove_position(parts[1])
                print("OK")

            else:
                print("Unknown command. Type 'help'")

        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
