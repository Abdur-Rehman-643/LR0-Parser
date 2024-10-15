# LR(0) Parser

## Overview

This repository contains a Python implementation of an LR(0) parser. The parser constructs the canonical collection of LR(0) items and generates the action and goto tables necessary for parsing input strings based on a given context-free grammar.

### Features

- Constructs closure sets for LR(0) items.
- Generates action and goto tables for parsing.
- Parses input strings with detailed step-by-step output, including stack and input status.

## Getting Started

### Prerequisites

Make sure you have Python 3 installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).

### Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Abdur-Rehman-643/LR0-Parser.git
   ```

2. Navigate to the project directory:

   ```bash
   cd LR0-Parser
   ```

### Usage

You can run the parser by executing the following command:

```bash
python lr0_parser.py
```

This will parse the predefined input string `['id', '*', 'id', '+', 'id']` based on the specified grammar.

### Grammar Example

The current implementation uses the following grammar:

```
S' -> S
S  -> E
E  -> E + T
E  -> T
T  -> T * F
T  -> F
F  -> ( E )
F  -> id
```

### Output

The output includes:

- Closure sets for each state.
- Action and goto tables.
- Step-by-step parsing results with stack, input, action, and output.

### Contributions

Contributions are welcome! If you have suggestions for improvements or enhancements, feel free to open an issue or submit a pull request.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Author

[Abdur Rehman](https://github.com/Abdur-Rehman-643)
