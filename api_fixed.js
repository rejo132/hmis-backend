import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor to include JWT token in all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Ensure page is a number
    if (config.params && config.params.page) {
      config.params.page = Number(config.params.page);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear localStorage
      localStorage.removeItem('access_token');
      // You might want to dispatch a logout action here
      // window.location.href = '/login'; // Or redirect to login
    }
    return Promise.reject(error);
  }
);

export const loginAPI = (credentials) => api.post('/api/login', credentials);
export const registerAPI = (data) => api.post('/api/register', data);
export const getPatients = (page = 1) => api.get(`/api/patients`, { params: { page } });
export const getPatient = (id) => api.get(`/api/patients/${id}`);
export const createPatient = (data) => api.post('/api/patients', data);
export const updatePatient = (id, data) => api.put(`/api/patients/${id}`, data);
export const getAppointments = (page = 1) => api.get(`/api/appointments`, { params: { page } });
export const createAppointment = (data) => api.post('/api/appointments', data);
export const getRecords = (page = 1) => api.get(`/api/records`, { params: { page } });
export const createMedicalRecord = (data) => api.post('/api/records', data);
export const getBills = (page = 1) => api.get(`/api/bills`, { params: { page } });
export const createBill = (data) => api.post('/api/bills', data);
export const updateBill = (billId, data) => api.put(`/api/bills/${billId}`, data);
export const deleteBill = (billId) => api.delete(`/api/bills/${billId}`);
export const processRefund = (data) => api.post('/api/bills/refund', data);
export const submitClaim = (data) => api.post('/api/bills/claim', data);
export const createLabOrder = (data) => api.post('/api/lab-orders', data);
export const getLabOrders = () => api.get('/api/lab-orders');
export const createRadiologyOrder = (data) => api.post('/api/radiology-orders', data);
export const getRadiologyOrders = () => api.get('/api/radiology-orders');
export const getEmployees = () => api.get('/api/employees');
export const createEmployee = (data) => api.post('/api/employees', data);
export const updateEmployee = (id, data) => api.put(`/api/employees/${id}`, data);
export const getFinanceExpenses = () => api.get('/api/finance/expenses');
export const getFinanceReimbursements = () => api.get('/api/finance/reimbursements');
export const getFinancePayroll = () => api.get('/api/finance/payroll');
export const createExpense = (data) => api.post('/api/finance/expenses', data);
export const getInventory = () => api.get('/api/inventory');
export const createInventory = (data) => api.post('/api/inventory', data);
export const updateInventory = (id, data) => api.put(`/api/inventory/${id}`, data);
export const dispenseMedication = (data) => api.post('/api/inventory/dispense', data);
export const createMedication = (data) => api.post('/api/medications', data);
export const createSample = (data) => api.post('/api/lab-samples', data);
export const getSecurityLogs = () => api.get('/api/security-logs');
export const getShifts = () => api.get('/api/shifts');
export const createShift = (data) => api.post('/api/shifts', data);
export const getSettings = () => api.get('/api/settings');
export const updateSettings = (data) => api.put('/api/settings', data);
export const getUserRoles = () => api.get('/api/users/roles');
export const updateUserRole = (data) => api.put('/api/users/roles', data);
export const createVitals = (data) => api.post('/api/vitals', data);
export const getAuditLogs = () => api.get('/api/audit-logs');
export const getAssets = () => api.get('/api/assets');
export const scheduleMaintenance = (data) => api.post('/api/assets/maintenance', data);
export const getBeds = () => api.get('/api/beds');
export const reserveBed = (data) => api.post('/api/beds/reserve', data);
export const getCommunicationSettings = () => api.get('/api/communication-settings');
export const addCommunication = (data) => api.post('/api/communications', data);
export const toggleCommunicationSetting = (data) => api.put('/api/communication-settings', data);

export default api;