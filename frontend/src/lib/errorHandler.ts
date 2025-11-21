/**
 * Safely extract error message from API error response
 * Handles various error response formats
 */
export const getErrorMessage = (error: any, defaultMessage = 'An error occurred'): string => {
  if (!error) return defaultMessage;

  // If error is already a string
  if (typeof error === 'string') return error;

  // Check response data
  const data = error.response?.data;
  
  if (!data) {
    return error.message || defaultMessage;
  }

  // If data is a string
  if (typeof data === 'string') return data;

  // If data is an object, try various common error fields
  if (typeof data === 'object') {
    // Try common error message fields
    if (typeof data.error === 'string') return data.error;
    if (typeof data.message === 'string') return data.message;
    if (typeof data.detail === 'string') return data.detail;
    
    // If error is an object with message
    if (data.error && typeof data.error === 'object') {
      if (typeof data.error.message === 'string') return data.error.message;
    }

    // If there are field-specific errors (validation errors)
    if (data.errors && typeof data.errors === 'object') {
      const firstError = Object.values(data.errors)[0];
      if (Array.isArray(firstError) && firstError.length > 0) {
        return String(firstError[0]);
      }
      if (typeof firstError === 'string') return firstError;
    }

    // Try to stringify if it's a simple object
    try {
      const keys = Object.keys(data);
      if (keys.length > 0) {
        const firstKey = keys[0];
        const firstValue = data[firstKey];
        if (typeof firstValue === 'string') {
          return `${firstKey}: ${firstValue}`;
        }
        if (Array.isArray(firstValue) && firstValue.length > 0) {
          return `${firstKey}: ${firstValue[0]}`;
        }
      }
    } catch (e) {
      // Fall through to default
    }
  }

  // Last resort
  return error.message || defaultMessage;
};
