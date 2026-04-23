import { apiClient } from './client'

export interface ReportColumn {
  label: string
  fieldname: string
  fieldtype: string
  width: number
}

export interface ReportResult {
  columns: ReportColumn[]
  rows: Record<string, any>[]
  message?: string
}

function normaliseColumns(raw: any[]): ReportColumn[] {
  return raw.map((col, i) => {
    if (typeof col === 'string') {
      const parts = col.split(':')
      const label = parts[0] || `Col ${i}`
      return {
        label,
        fieldname: label.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
        fieldtype: parts[1] || 'Data',
        width: parts[2] ? parseInt(parts[2]) : 130,
      }
    }
    const label = col.label || col.fieldname || `Col ${i}`
    return {
      label,
      fieldname: col.fieldname || label.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
      fieldtype: col.fieldtype || 'Data',
      width: col.width || 130,
    }
  })
}

function normaliseRows(rows: any[], columns: ReportColumn[]): Record<string, any>[] {
  if (!rows.length) return []
  if (Array.isArray(rows[0])) {
    // Query Report returns value arrays — zip with column fieldnames
    return rows.map((row) =>
      Object.fromEntries(columns.map((col, i) => [col.fieldname, row[i]]))
    )
  }
  return rows
}

export async function runReport(
  reportName: string,
  filters: Record<string, any> = {}
): Promise<ReportResult> {
  const cleanFilters: Record<string, any> = {}
  for (const [k, v] of Object.entries(filters)) {
    if (v !== '' && v !== null && v !== undefined) cleanFilters[k] = v
  }

  const response = await apiClient.get('/api/method/frappe.desk.query_report.run', {
    params: {
      report_name: reportName,
      filters: JSON.stringify(cleanFilters),
      ignore_prepared_report: 1,
    },
  })

  const data = response.data.message ?? response.data
  const columns = normaliseColumns(data.columns ?? [])
  const rows = normaliseRows(data.result ?? [], columns)

  return { columns, rows, message: data.message }
}
