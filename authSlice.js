import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { loginAPI, registerAPI } from '../api/api'; // Use api.js client

export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password }, { rejectWithValue }) => {
    try {
      console.log('Sending login request:', { username, password });
      const response = await loginAPI({ username, password });
      console.log('Login response:', response.data);
      return response.data;
    } catch (err) {
      console.error('Login request failed:', err.message);
      return rejectWithValue(err.response?.data || { message: err.message });
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      console.log('Sending register request:', userData);
      const response = await registerAPI(userData);
      console.log('Register response:', response.data);
      return response.data;
    } catch (err) {
      console.error('Register request failed:', err.message);
      return rejectWithValue(err.response?.data || { message: err.message });
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    access_token: null,
    status: 'idle',
    error: null,
  },
  reducers: {
    logout: (state) => {
      state.user = null;
      state.access_token = null;
      state.status = 'idle';
      state.error = null;
      // Clear token from localStorage
      localStorage.removeItem('access_token');
    },
    // Add action to load token from localStorage on app startup
    loadTokenFromStorage: (state) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        state.access_token = token;
        // You might want to validate the token here or decode it to get user info
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = {
          username: action.payload.user?.username || 'Unknown', // Updated to access nested user
          role: action.payload.user?.role || 'Unknown', // Fix: Use action.payload.user.role
        };
        state.access_token = action.payload.access_token; // Fix: Use access_token
        state.error = null;
        // Save token to localStorage
        localStorage.setItem('access_token', action.payload.access_token);
      })
      .addCase(login.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload.message;
      })
      .addCase(register.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = {
          username: action.payload.user?.username || 'Unknown',
          role: action.payload.user?.role || 'Unknown', // Fix: Use action.payload.user.role
        };
        state.access_token = action.payload.access_token;
        state.error = null;
        // Save token to localStorage
        localStorage.setItem('access_token', action.payload.access_token);
      })
      .addCase(register.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload.message;
      });
  },
});

export const { logout, loadTokenFromStorage } = authSlice.actions;
export default authSlice.reducer;