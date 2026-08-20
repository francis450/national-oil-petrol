import { ref, computed, type Ref } from 'vue'

interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => string | null
  type?: 'email' | 'number' | 'url' | 'date'
}

interface ValidationErrors {
  [key: string]: string
}

interface FieldConfig {
  value: Ref<any>
  rules?: ValidationRule[]
  label?: string
}

export function useFormValidation(fields: Record<string, FieldConfig>) {
  const errors = ref<ValidationErrors>({})
  const isValid = ref(true)

  // Validate a single field
  const validateField = (fieldName: string): string | null => {
    const field = fields[fieldName]
    if (!field) return null

    const value = field.value.value
    const rules = field.rules || []
    const label = field.label || fieldName

    for (const rule of rules) {
      // Required validation
      if (rule.required && (value === null || value === undefined || value === '')) {
        return `${label} is required`
      }

      // Skip other validations if value is empty and not required
      if (value === null || value === undefined || value === '') {
        continue
      }

      // Min length validation
      if (rule.minLength !== undefined && String(value).length < rule.minLength) {
        return `${label} must be at least ${rule.minLength} characters`
      }

      // Max length validation
      if (rule.maxLength !== undefined && String(value).length > rule.maxLength) {
        return `${label} must be less than ${rule.maxLength} characters`
      }

      // Pattern validation
      if (rule.pattern && !rule.pattern.test(String(value))) {
        return `${label} format is invalid`
      }

      // Type validation
      if (rule.type) {
        switch (rule.type) {
          case 'email':
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/i
            if (!emailPattern.test(String(value))) {
              return `${label} must be a valid email address`
            }
            break
          case 'number':
            if (isNaN(Number(value))) {
              return `${label} must be a valid number`
            }
            break
          case 'url':
            try {
              new URL(String(value))
            } catch {
              return `${label} must be a valid URL`
            }
            break
          case 'date':
            if (isNaN(Date.parse(String(value)))) {
              return `${label} must be a valid date`
            }
            break
        }
      }

      // Custom validation
      if (rule.custom) {
        const error = rule.custom(value)
        if (error) {
          return error
        }
      }
    }

    return null
  }

  // Validate all fields
  const validate = (): boolean => {
    isValid.value = true
    errors.value = {}

    for (const fieldName of Object.keys(fields)) {
      const error = validateField(fieldName)
      if (error) {
        errors.value[fieldName] = error
        isValid.value = false
      }
    }

    return isValid.value
  }

  // Validate on field change
  const validateOnChange = (fieldName: string) => {
    const error = validateField(fieldName)
    if (error) {
      errors.value[fieldName] = error
    } else {
      delete errors.value[fieldName]
    }
  }

  // Clear errors
  const clearErrors = () => {
    errors.value = {}
    isValid.value = true
  }

  // Set error for a specific field
  const setError = (fieldName: string, message: string) => {
    errors.value[fieldName] = message
    isValid.value = false
  }

  // Check if a specific field has an error
  const hasError = (fieldName: string): boolean => {
    return !!errors.value[fieldName]
  }

  // Get error message for a specific field
  const getError = (fieldName: string): string | undefined => {
    return errors.value[fieldName]
  }

  return {
    errors,
    isValid,
    validate,
    validateField,
    validateOnChange,
    clearErrors,
    setError,
    hasError,
    getError,
  }
}

// Common validation rules
export const validators = {
  required: (label?: string): ValidationRule => ({ required: true, label }),
  minLength: (min: number, label?: string): ValidationRule => ({ minLength: min, label }),
  maxLength: (max: number, label?: string): ValidationRule => ({ maxLength: max, label }),
  email: (label?: string): ValidationRule => ({ type: 'email', label }),
  number: (label?: string): ValidationRule => ({ type: 'number', label }),
  url: (label?: string): ValidationRule => ({ type: 'url', label }),
  date: (label?: string): ValidationRule => ({ type: 'date', label }),
  pattern: (regex: RegExp, label?: string): ValidationRule => ({ pattern: regex, label }),
  custom: (fn: (value: any) => string | null, label?: string): ValidationRule => ({ custom: fn, label }),
}
