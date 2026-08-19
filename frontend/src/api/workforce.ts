import { apiClient } from './client'

export interface EmployeeRow {
  name: string
  employee_name?: string
  department?: string
  designation?: string
  company?: string
  status?: string
  doctype: 'Employee'
  label?: string
}

export interface AttendanceRow {
  name: string
  employee?: string
  employee_name?: string
  attendance_date: string
  department?: string
  status?: string
  company?: string
  doctype: 'Attendance'
  label?: string
}

export interface LeaveApplicationRow {
  name: string
  employee?: string
  employee_name?: string
  department?: string
  leave_type?: string
  from_date: string
  to_date?: string
  status?: string
  doctype: 'Leave Application'
  label?: string
}

export interface ShiftTypeRow {
  name: string
  start_time?: string
  end_time?: string
  enable_auto_attendance?: number
  disabled?: number
  doctype: 'Shift Type'
  label?: string
}

export interface ShiftAssignmentRow {
  name: string
  employee?: string
  employee_name?: string
  shift_type?: string
  start_date: string
  end_date?: string
  status?: string
  reconciliation_status?: 'Open' | 'Closed' | 'Verified'
  total_expected_sales?: number
  closed_at?: string
  doctype: 'Shift Assignment'
  label?: string
}

export interface CompanyRow {
  name: string
  company_name?: string
  doctype: 'Company'
  label?: string
}

interface ListWorkforceResponse<T> {
  doctype: string
  count: number
  records: T[]
}

const listWorkforceRecords = async <T>(
  doctype: 'Employee' | 'Attendance' | 'Leave Application' | 'Shift Type' | 'Shift Assignment' | 'Company',
  params: Record<string, any> = {},
) => {
  const response = await apiClient.get('/api/method/national_oil.api.workforce.list_workforce_records', {
    params: {
      doctype,
      limit_page_length: 50,
      ...params,
    },
  })

  return (response.data.message as ListWorkforceResponse<T>).records
}

export const workforceApi = {
  async listEmployees() {
    return await listWorkforceRecords<EmployeeRow>('Employee')
  },

  async listAttendance(status?: string) {
    return await listWorkforceRecords<AttendanceRow>('Attendance', {
      ...(status ? { status } : {}),
    })
  },

  async listLeaveApplications(status?: string) {
    return await listWorkforceRecords<LeaveApplicationRow>('Leave Application', {
      ...(status ? { status } : {}),
    })
  },

  async listShiftTypes() {
    return await listWorkforceRecords<ShiftTypeRow>('Shift Type')
  },

  async listShiftAssignments(status?: string) {
    return await listWorkforceRecords<ShiftAssignmentRow>('Shift Assignment', {
      ...(status ? { status } : {}),
      limit_page_length: 100,
    })
  },

  async listCompanies() {
    return await listWorkforceRecords<CompanyRow>('Company')
  },
}
