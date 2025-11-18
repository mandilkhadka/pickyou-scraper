# Project Rules and Guidelines

## Code Style

- Follow PEP 8 Python style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to all functions and classes

## Error Handling

- Always handle exceptions gracefully
- Use try-except blocks for network requests and file operations
- Log errors with descriptive messages
- Never let the scraper crash silently - always print error messages
- Return `None` or empty lists/strings instead of raising exceptions where appropriate

## Rate Limiting

- Default delay between requests: 1.0 second
- Respect Shopify API rate limits
- Implement exponential backoff for retries
- Maximum retries: 3 attempts
- Handle HTTP 429 (Too Many Requests) responses appropriately

## Data Format Validation

- All products must have required fields: `platform`, `id`, `name`, `price`
- Price must be an integer (convert from float if needed)
- Sizes array must contain at least one item
- Brand object must have structure: `{id, name, sub_name}` (can be null)
- Image URLs must be valid strings (can be empty)
- Platform URL must be constructed correctly from product handle

## Testing Requirements

- Write unit tests for all core functions
- Test pagination logic with mock responses
- Test parser transformation with sample Shopify data
- Test error handling scenarios
- Test file I/O operations
- Use pytest for testing framework
- Aim for >80% code coverage

## File Organization

- Keep source code in `src/` directory
- Keep tests in `tests/` directory
- Keep output data in `data/` directory
- Use `__init__.py` files to make directories Python packages

## Output Format

- Final JSON must have structure: `{"items": [...]}`
- Each item must match the custom format specification
- JSON should be pretty-printed with 2-space indentation
- Use UTF-8 encoding for all file operations

## Dependencies

- Keep dependencies minimal and well-maintained
- Pin major version numbers in requirements.txt
- Document why each dependency is needed
- Avoid unnecessary external libraries

