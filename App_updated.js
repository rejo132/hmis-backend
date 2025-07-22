import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout, loadTokenFromStorage } from './slices/authSlice';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import PatientForm from './components/PatientForm';
import AppointmentForm from './components/AppointmentForm';
import BillForm from './components/BillForm';
import RecordForm from './components/RecordForm';
import AppointmentsCalendar from './components/AppointmentsCalendar';
import EMR from './components/EMR';
import LabOrderForm from './components/LabOrderForm';
import RadiologyForm from './components/RadiologyForm';
import BedManagement from './components/BedManagement';
import AssetManagement from './components/AssetManagement';
import InventoryManagement from './components/InventoryManagement';
import EmployeeManagement from './components/EmployeeManagement';
import ReportsDashboard from './components/ReportsDashboard';
import PatientPortal from './components/PatientPortal';
import DoctorPortal from './components/DoctorPortal';
import CommunicationSettings from './components/CommunicationSettings';
import VitalsTracking from './components/VitalsTracking';
import MedicationAdministration from './components/MedicationAdministration';
import ShiftManagement from './components/ShiftManagement';
import SampleCollection from './components/SampleCollection';
import ReceptionManagement from './components/ReceptionManagement';
import BillingManagement from './components/BillingManagement';
import AuditLogs from './components/AuditLogs';
import SystemSettings from './components/SystemSettings';
import UserRoleManagement from './components/UserRoleManagement';
import SecurityLogs from './components/SecurityLogs';
import FinanceManagement from './components/FinanceManagement';

const App = () => {
  const dispatch = useDispatch();
  const { user, status } = useSelector((state) => state.auth || {});
  console.log('App.js: user=', user, 'authStatus=', status);

  // Load token from localStorage on app startup
  useEffect(() => {
    dispatch(loadTokenFromStorage());
  }, [dispatch]);

  const roleColor = user?.role === 'Doctor' ? 'bg-blue-600' : 
                   user?.role === 'Nurse' ? 'bg-green-600' : 
                   user?.role === 'Admin' ? 'bg-gray-600' : 
                   user?.role === 'Lab' ? 'bg-red-600' : 
                   user?.role === 'Patient' ? 'bg-indigo-600' : 
                   user?.role === 'Pharmacist' ? 'bg-purple-600' :
                   user?.role === 'Receptionist' ? 'bg-teal-600' :
                   user?.role === 'Billing' ? 'bg-yellow-600' :
                   user?.role === 'IT' ? 'bg-orange-600' :
                   user?.role === 'Accountant' ? 'bg-pink-600' : 'bg-gray-200';

  const handleLogout = () => {
    dispatch(logout()); // This now handles localStorage cleanup automatically
  };

  // Default redirect path when user is undefined or role is unknown
  const getRedirectPath = () => {
    if (!user || !user.role) return '/dashboard';
    switch (user.role) {
      case 'Admin':
        return '/dashboard';
      case 'Patient':
        return '/patient-portal';
      case 'Doctor':
        return '/doctor-portal';
      case 'Nurse':
        return '/vitals';
      case 'Lab':
        return '/lab-orders';
      case 'Receptionist':
        return '/reception';
      case 'Billing':
        return '/billing';
      case 'IT':
        return '/users/roles';
      case 'Accountant':
        return '/finance';
      case 'Pharmacist':
        return '/inventory';
      default:
        return '/dashboard';
    }
  };

  return (
    <ErrorBoundary>
      <Router>
        <div className="flex min-h-screen flex-col">
          {/* Loading Indicator */}
          {status === 'loading' && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 z-50">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
            </div>
          )}
          {/* Sticky Header */}
          {status === 'succeeded' && user && (
            <header className={`sticky top-0 z-20 ${roleColor} text-white p-4 shadow-md`}>
              <div className="container mx-auto flex justify-between items-center">
                <h1 className="text-xl font-bold">HMIS</h1>
                <div className="flex items-center space-x-4">
                  <span className="text-sm">{user.username || 'User'} ({user.role || 'Unknown'})</span>
                  <button onClick={handleLogout} className="btn-secondary text-sm">
                    <svg className="w-5 h-5 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h3a3 3 0 013 3v1"></path>
                    </svg>
                    Logout
                  </button>
                </div>
              </div>
            </header>
          )}
          <div className="flex flex-1">
            {/* Sidebar Navigation */}
            <nav className={`fixed top-0 left-0 h-full w-64 ${roleColor} text-white p-4 pt-16 md:block hidden z-10 shadow-lg`}>
              <ul className="space-y-2">
                <li>
                  <NavLink to="/dashboard" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                    </svg>
                    Dashboard
                  </NavLink>
                </li>
                {(user?.role === 'Admin' || user?.role === 'Receptionist') && (
                  <li>
                    <NavLink to="/patients/new" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                      </svg>
                      Patients
                    </NavLink>
                  </li>
                )}
                {(user?.role === 'Admin' || user?.role === 'Receptionist') && (
                  <li>
                    <NavLink to="/reception" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path>
                      </svg>
                      Reception
                    </NavLink>
                  </li>
                )}
                {(user?.role === 'Admin' || user?.role === 'Nurse') && (
                  <li>
                    <NavLink to="/beds" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                      </svg>
                      Beds
                    </NavLink>
                  </li>
                )}
                {(user?.role === 'Admin' || user?.role === 'Pharmacist') && (
                  <li>
                    <NavLink to="/inventory" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                      </svg>
                      Inventory
                    </NavLink>
                  </li>
                )}
                {(user?.role === 'Admin') && (
                  <>
                    <li>
                      <NavLink to="/employees" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v2h5m-2-2a3 3 0 005.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                        </svg>
                        Employees
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/assets" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Assets
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/audit-logs" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Audit Logs
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/settings" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37a1.724 1.724 0 002.572-1.065z"></path>
                        </svg>
                        Settings
                      </NavLink>
                    </li>
                  </>
                )}
                {(user?.role === 'IT') && (
                  <>
                    <li>
                      <NavLink to="/users/roles" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                        </svg>
                        User Roles
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/security-logs" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 1.104-.896 2-2 2s-2-.896-2-2 2-4 2-4 2 .896 2 2zm0 0c0 1.104-.896 2-2 2s-2-.896-2-2 2-4 2-4 2 .896 2 2zm0 0c0 1.104-.896 2-2 2s-2-.896-2-2 2-4 2-4 2 .896 2 2z"></path>
                        </svg>
                        Security Logs
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/settings" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37a1.724 1.724 0 002.572-1.065z"></path>
                        </svg>
                        System Maintenance
                      </NavLink>
                    </li>
                  </>
                )}
                {(user?.role === 'Admin' || user?.role === 'Accountant') && (
                  <li>
                    <NavLink to="/finance" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
                      </svg>
                      Finance
                    </NavLink>
                  </li>
                )}
                <li>
                  <NavLink to="/appointments" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Appointments
                  </NavLink>
                </li>
                {(user?.role === 'Admin' || user?.role === 'Doctor' || user?.role === 'Nurse' || user?.role === 'Lab') && (
                  <>
                    <li>
                      <NavLink to="/emr" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                        </svg>
                        EMR
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/lab-orders" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                        </svg>
                        Lab Orders
                      </NavLink>
                    </li>
                    {(user?.role === 'Nurse') && (
                      <>
                        <li>
                          <NavLink to="/vitals" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                            </svg>
                            Vitals
                          </NavLink>
                        </li>
                        <li>
                          <NavLink to="/medications" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                            Medications
                          </NavLink>
                        </li>
                        <li>
                          <NavLink to="/shifts" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l4 2m-8-2h4m-6 8h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                            Shifts
                          </NavLink>
                        </li>
                      </>
                    )}
                    {(user?.role === 'Lab') && (
                      <li>
                        <NavLink to="/lab-samples" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16l-4-4m0 0l4-4m-4 4h18"></path>
                          </svg>
                          Sample Collection
                        </NavLink>
                      </li>
                    )}
                  </>
                )}
                {(user?.role === 'Admin' || user?.role === 'Doctor') && (
                  <li>
                    <NavLink to="/radiology" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                      Radiology
                    </NavLink>
                  </li>
                )}
                {(user?.role === 'Admin' || user?.role === 'Billing') && (
                  <li>
                    <NavLink to="/billing" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
                      </svg>
                      Billing
                    </NavLink>
                  </li>
                )}
                <li>
                  <NavLink to="/reports" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Reports
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/communications" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                    Communications
                  </NavLink>
                </li>
                {user?.role === 'Patient' && (
                  <li>
                    <NavLink to="/patient-portal" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                      </svg>
                      Patient Portal
                    </NavLink>
                  </li>
                )}
                {(user?.role === 'Admin' || user?.role === 'Doctor') && (
                  <li>
                    <NavLink to="/doctor-portal" className={({ isActive }) => `flex items-center py-2 px-3 rounded-md hover:bg-opacity-80 transition-colors ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                      </svg>
                      Doctor Portal
                    </NavLink>
                  </li>
                )}
              </ul>
            </nav>
            {/* Main Content */}
            <main className="flex-1 p-4 md:ml-64 mt-16">
              <Routes>
                <Route
                  path="/"
                  element={
                    status === 'loading' ? (
                      <div>Loading...</div>
                    ) : status === 'succeeded' && user ? (
                      <Navigate to={getRedirectPath()} />
                    ) : (
                      <Login />
                    )
                  }
                />
                <Route
                  path="/dashboard"
                  element={status === 'succeeded' && user ? <Dashboard /> : <Navigate to="/" />}
                />
                <Route
                  path="/patients/new"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Receptionist') ? <PatientForm /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/appointments/new"
                  element={status === 'succeeded' && user ? <AppointmentForm /> : <Navigate to="/" />}
                />
                <Route
                  path="/appointments"
                  element={status === 'succeeded' && user ? <AppointmentsCalendar /> : <Navigate to="/" />}
                />
                <Route
                  path="/bills/new"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Billing') ? <BillForm /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/billing"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Billing') ? <BillingManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/records/new"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Doctor' || user.role === 'Nurse') ? <RecordForm /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/emr"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Doctor' || user.role === 'Nurse' || user.role === 'Lab') ? <EMR /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/lab-orders"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Doctor' || user.role === 'Lab') ? <LabOrderForm /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/lab-samples"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Lab') ? <SampleCollection /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/radiology"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Doctor') ? <RadiologyForm /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/beds"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Nurse') ? <BedManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/assets"
                  element={status === 'succeeded' && user && user.role === 'Admin' ? <AssetManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/inventory"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Pharmacist') ? <InventoryManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/employees"
                  element={status === 'succeeded' && user && user.role === 'Admin' ? <EmployeeManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/vitals"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Nurse') ? <VitalsTracking /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/medications"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Nurse') ? <MedicationAdministration /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/shifts"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Nurse') ? <ShiftManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/reception"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Receptionist') ? <ReceptionManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/audit-logs"
                  element={status === 'succeeded' && user && user.role === 'Admin' ? <AuditLogs /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/settings"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'IT') ? <SystemSettings /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/users/roles"
                  element={status === 'succeeded' && user && user.role === 'IT' ? <UserRoleManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/security-logs"
                  element={status === 'succeeded' && user && user.role === 'IT' ? <SecurityLogs /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/finance"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Accountant') ? <FinanceManagement /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/reports"
                  element={status === 'succeeded' && user ? <ReportsDashboard /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/communications"
                  element={status === 'succeeded' && user ? <CommunicationSettings /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="/patient-portal"
                  element={status === 'succeeded' && user && user.role === 'Patient' ? <PatientPortal /> : <Navigate to="/" />}
                />
                <Route
                  path="/doctor-portal"
                  element={status === 'succeeded' && user && (user.role === 'Admin' || user.role === 'Doctor') ? <DoctorPortal /> : <Navigate to="/dashboard" />}
                />
                <Route
                  path="*"
                  element={<Navigate to="/" />}
                />
              </Routes>
            </main>
            {/* Mobile Navigation */}
            <nav className={`fixed bottom-0 left-0 w-full ${roleColor} text-white p-2 md:hidden shadow-lg`}>
              <ul className="flex justify-around text-sm">
                <li>
                  <NavLink to="/dashboard" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                    </svg>
                    Dashboard
                  </NavLink>
                </li>
                {(user?.role === 'Admin' || user?.role === 'Receptionist') && (
                  <>
                    <li>
                      <NavLink to="/patients/new" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                        </svg>
                        Patients
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/reception" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path>
                        </svg>
                        Reception
                      </NavLink>
                    </li>
                  </>
                )}
                {(user?.role === 'Admin' || user?.role === 'Nurse') && (
                  <li>
                    <NavLink to="/beds" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                      </svg>
                      Beds
                    </NavLink>
                  </li>
                )}
                {(user?.role === 'Admin' || user?.role === 'Pharmacist') && (
                  <li>
                    <NavLink to="/inventory" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                      </svg>
                      Inventory
                    </NavLink>
                  </li>
                )}
                <li>
                  <NavLink to="/appointments" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Appointments
                  </NavLink>
                </li>
                {(user?.role === 'Admin' || user?.role === 'Doctor' || user?.role === 'Nurse' || user?.role === 'Lab') && (
                  <>
                    <li>
                      <NavLink to="/emr" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                        </svg>
                        EMR
                      </NavLink>
                    </li>
                    <li>
                      <NavLink to="/lab-orders" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                        </svg>
                        Lab Orders
                      </NavLink>
                    </li>
                    {(user?.role === 'Nurse') && (
                      <>
                        <li>
                          <NavLink to="/vitals" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                            </svg>
                            Vitals
                          </NavLink>
                        </li>
                        <li>
                          <NavLink to="/medications" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                            Medications
                          </NavLink>
                        </li>
                      </>
                    )}
                    {(user?.role === 'Lab') && (
                      <li>
                        <NavLink to="/lab-samples" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16l-4-4m0 0l4-4m-4 4h18"></path>
                          </svg>
                          Samples
                        </NavLink>
                      </li>
                    )}
                  </>
                )}
                {(user?.role === 'Admin' || user?.role === 'Billing') && (
                  <li>
                    <NavLink to="/billing" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
                      </svg>
                      Billing
                    </NavLink>
                  </li>
                )}
                <li>
                  <NavLink to="/reports" className={({ isActive }) => `flex flex-col items-center py-2 ${isActive ? 'bg-white bg-opacity-20' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Reports
                  </NavLink>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </Router>
    </ErrorBoundary>
  );
};

export default App;