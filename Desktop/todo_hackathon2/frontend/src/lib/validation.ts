/**
 * Form Validation Utility Functions - Phase II Todo Hackathon
 * Client-side validation rules
 */

/**
 * Validate email format
 * @returns Error message or null if valid
 */
export function validateEmail(email: string): string | null {
  if (!email || email.trim().length === 0) {
    return 'Email is required';
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Please enter a valid email address';
  }

  return null;
}

/**
 * Validate password strength
 * @returns Error message or null if valid
 */
export function validatePassword(password: string): string | null {
  if (!password || password.length === 0) {
    return 'Password is required';
  }

  if (password.length < 8) {
    return 'Password must be at least 8 characters long';
  }

  return null;
}

/**
 * Validate task title
 * @returns Error message or null if valid
 */
export function validateTitle(title: string): string | null {
  if (!title || title.trim().length === 0) {
    return 'Title is required';
  }

  if (title.trim().length > 200) {
    return 'Title must be 200 characters or less';
  }

  return null;
}

/**
 * Validate task description (optional field)
 * @returns Error message or null if valid
 */
export function validateDescription(description: string): string | null {
  if (description && description.length > 1000) {
    return 'Description must be 1000 characters or less';
  }

  return null;
}

/**
 * Validate name field (optional)
 * @returns Error message or null if valid
 */
export function validateName(name: string): string | null {
  if (name && name.length > 100) {
    return 'Name must be 100 characters or less';
  }

  return null;
}
