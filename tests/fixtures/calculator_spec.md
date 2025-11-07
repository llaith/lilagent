# CLI Calculator Specification

Create a command-line calculator tool that can perform basic arithmetic operations.

## Requirements

The calculator should:
- Accept two numbers and an operation from the command line
- Support addition, subtraction, multiplication, and division
- Handle division by zero gracefully
- Provide clear error messages for invalid inputs
- Be installable as a Python package
- Include tests for all operations

## Usage Example

```bash
calculator add 5 3
# Output: 8.0

calculator multiply 4 2.5
# Output: 10.0

calculator divide 10 0
# Error: Cannot divide by zero
```

## Technical Details

- Language: Python 3.11+
- Package name: simple_calculator
- CLI tool name: calculator
- Use argparse for command-line interface
- Include pytest tests
