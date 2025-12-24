# calculator.py

def add(x, y):
    """This function adds two numbers"""
    return x + y


def subtract(x, y):
    """This function subtracts two numbers"""
    return x - y


def multiply(x, y):
    """This function multiplies two numbers"""
    return x * y


def divide(x, y):
    """This function divides two numbers"""
    if y == 0:
        return "Error! Division by zero."
    return x / y


# Main execution block
if __name__ == "__main__":
    # We will use predefined numbers for the CI/CD run
    num1 = 10
    num2 = 5

    print(f"Numbers are: {num1} and {num2}")

    # Perform and print all operations
    print(f"{num1} + {num2} = {add(num1, num2)}")
    print(f"{num1} - {num2} = {subtract(num1, num2)}")
    print(f"{num1} * {num2} = {multiply(num1, num2)}")
    print(f"{num1} / {num2} = {divide(num1, num2)}")

    # Test division by zero
    print(f"\nTesting division by zero:")
    print(f"{num1} / 0 = {divide(num1, 0)}")
