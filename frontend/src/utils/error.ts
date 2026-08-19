const stripHtml = (value: string) => value.replace(/<[^>]*>/g, '').trim()

/**
 * Frappe's REST v1 endpoints (/api/resource/...) put the human-readable message from
 * frappe.throw() inside response.data._server_messages — a JSON-encoded array of JSON
 * strings — not response.data.message. Checking only .message silently drops these,
 * including common validation errors like HRMS's MultipleShiftError.
 */
export const extractErrorMessage = (error: any): string => {
  const data = error?.response?.data

  const serverMessages = data?._server_messages
  if (serverMessages) {
    try {
      const parsed: string[] = JSON.parse(serverMessages)
      const messages = parsed
        .map((raw) => {
          try {
            return JSON.parse(raw)?.message
          } catch {
            return raw
          }
        })
        .filter(Boolean)
        .map(stripHtml)
      if (messages.length) return messages.join(' ')
    } catch {
      // fall through to other fields
    }
  }

  if (data?.message) return stripHtml(String(data.message))
  if (data?.exc_type && data?.exception) return stripHtml(String(data.exception))
  if (error?.message) return error.message

  return 'Something went wrong. Please try again.'
}
