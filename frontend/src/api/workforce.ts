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

interface ListWorkforceResponse<T> {
  doctype: string
  count: number
  records: T[]
}

const listWorkforceRecords = async <T>(doctype: 'Employee' | 'Attendance' | 'Leave Application', params: Record<string, any> = {}) => {
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
}
