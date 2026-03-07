// ScamShield authentication & shared UI helpers
// Handles: navigation, year, spinner & toast + login/register form validation
// Connected to real /api/login and /api/register backend endpoints.

(function () {
  const global = (window.ScamShield = window.ScamShield || {});

  // ── Backend base URL (change in production) ──
  const API_BASE = window.SCAMSHIELD_API_BASE || 'http://127.0.0.1:8000';

  function $(id) {
    return document.getElementById(id);
  }

  function initNav() {
    const toggle = $('nav-toggle');
    const menu = $('nav-menu');
    if (!toggle || !menu) return;
    toggle.addEventListener('click', function () {
      menu.classList.toggle('open');
    });
  }

  function initYear() {
    const yearEl = $('year');
    if (yearEl) {
      yearEl.textContent = new Date().getFullYear();
    }
  }

  function showSpinner() {
    const spinner = $('global-spinner');
    if (spinner) spinner.classList.add('visible');
  }

  function hideSpinner() {
    const spinner = $('global-spinner');
    if (spinner) spinner.classList.remove('visible');
  }

  function showToast(options) {
    const { type = 'info', title = '', message = '', timeout = 3500 } = options || {};
    const container = $('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;

    const pill = document.createElement('div');
    pill.className = 'toast-pill';
    pill.textContent = type === 'success' ? '✓' : type === 'error' ? '!' : 'ℹ';

    const body = document.createElement('div');
    body.className = 'toast-body';
    const titleEl = document.createElement('div');
    titleEl.className = 'toast-title';
    titleEl.textContent = title || (type === 'success' ? 'Success' : type === 'error' ? 'Error' : 'Notice');
    const msgEl = document.createElement('div');
    msgEl.className = 'toast-message';
    msgEl.textContent = message;
    body.appendChild(titleEl);
    body.appendChild(msgEl);

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'toast-close';
    close.textContent = '×';
    close.addEventListener('click', function () {
      container.removeChild(toast);
    });

    toast.appendChild(pill);
    toast.appendChild(body);
    toast.appendChild(close);
    container.appendChild(toast);

    if (timeout > 0) {
      setTimeout(function () {
        if (toast.parentNode === container) {
          container.removeChild(toast);
        }
      }, timeout);
    }
  }

  global.API_BASE = API_BASE;
  global.initCommonUI = function () {
    initNav();
    initYear();
  };
  global.showSpinner = showSpinner;
  global.hideSpinner = hideSpinner;
  global.showToast = showToast;

  function handleRedirectToast() {
    try {
      const params = new URLSearchParams(window.location.search);
      const from = params.get('from');
      if (!from) return;

      let message = '';
      if (from === 'scan') {
        message = 'Please login to scan suspicious messages and URLs.';
      } else if (from === 'report') {
        message = 'Please login before submitting a scam report.';
      } else if (from === 'dashboard') {
        message = 'Please login to access your ScamShield dashboard.';
      }

      if (message) {
        showToast({
          type: 'info',
          title: 'Authentication required',
          message: message,
        });
      }
    } catch (err) {
      // Ignore query parsing errors
    }
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function evaluatePasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    return score;
  }

  function updatePasswordStrengthUI(password) {
    const bars = document.querySelectorAll('.password-bar');
    const label = $('passwordStrengthLabel');
    if (!bars.length || !label) return;

    bars.forEach(function (bar) {
      bar.classList.remove('active-weak', 'active-medium', 'active-strong');
    });

    const score = evaluatePasswordStrength(password);
    if (!password) {
      label.textContent = 'Password strength: —';
      return;
    }

    if (score <= 1) {
      bars[0].classList.add('active-weak');
      label.textContent = 'Password strength: Weak – add more characters and symbols.';
    } else if (score === 2 || score === 3) {
      bars[0].classList.add('active-medium');
      bars[1].classList.add('active-medium');
      label.textContent = 'Password strength: Medium – you can still improve it.';
    } else {
      bars[0].classList.add('active-strong');
      bars[1].classList.add('active-strong');
      bars[2].classList.add('active-strong');
      label.textContent = 'Password strength: Strong – good choice for most accounts.';
    }
  }

  function handleLoginSubmit(e) {
    e.preventDefault();
    const email = $('loginEmail');
    const password = $('loginPassword');
    const emailError = $('loginEmailError');
    const passwordError = $('loginPasswordError');
    const generalError = $('loginGeneralError');

    if (!email || !password || !emailError || !passwordError || !generalError) return;

    emailError.textContent = '';
    passwordError.textContent = '';
    generalError.textContent = '';

    let valid = true;
    if (!email.value.trim()) {
      emailError.textContent = 'Email is required.';
      valid = false;
    } else if (!isValidEmail(email.value.trim())) {
      emailError.textContent = 'Please enter a valid email address.';
      valid = false;
    }

    if (!password.value) {
      passwordError.textContent = 'Password is required.';
      valid = false;
    } else if (password.value.length < 6) {
      passwordError.textContent = 'Password must be at least 6 characters.';
      valid = false;
    }

    if (!valid) return;

    showSpinner();

    fetch(API_BASE + '/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value.trim(), password: password.value }),
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (err) {
            throw new Error(err.detail || 'Login failed.');
          });
        }
        return res.json();
      })
      .then(function (data) {
        hideSpinner();

        // Store token + user data
        try {
          window.localStorage.setItem('scamshieldToken', data.access_token);
          window.localStorage.setItem(
            'scamshieldUser',
            JSON.stringify(data.user)
          );
        } catch (err) {
          // Storage error
        }

        showToast({
          type: 'success',
          title: 'Login successful',
          message: 'Redirecting to your dashboard.',
        });

        setTimeout(function () {
          window.location.href = 'dashboard.html';
        }, 900);
      })
      .catch(function (err) {
        hideSpinner();
        generalError.textContent = err.message || 'An error occurred. Please try again.';
      });
  }

  function handleRegisterSubmit(e) {
    e.preventDefault();
    const name = $('regName');
    const email = $('regEmail');
    const password = $('regPassword');
    const confirm = $('regConfirm');
    const nameError = $('regNameError');
    const emailError = $('regEmailError');
    const passwordError = $('regPasswordError');
    const confirmError = $('regConfirmError');

    if (!name || !email || !password || !confirm) return;

    nameError.textContent = '';
    emailError.textContent = '';
    passwordError.textContent = '';
    confirmError.textContent = '';

    let valid = true;

    if (!name.value.trim()) {
      nameError.textContent = 'Full name is required.';
      valid = false;
    }

    if (!email.value.trim()) {
      emailError.textContent = 'Email is required.';
      valid = false;
    } else if (!isValidEmail(email.value.trim())) {
      emailError.textContent = 'Please enter a valid email address.';
      valid = false;
    }

    if (!password.value) {
      passwordError.textContent = 'Password is required.';
      valid = false;
    } else if (password.value.length < 8) {
      passwordError.textContent = 'Use at least 8 characters for your password.';
      valid = false;
    }

    if (!confirm.value) {
      confirmError.textContent = 'Please confirm your password.';
      valid = false;
    } else if (confirm.value !== password.value) {
      confirmError.textContent = 'Passwords do not match.';
      valid = false;
    }

    if (!valid) return;

    showSpinner();

    fetch(API_BASE + '/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value.trim(),
        email: email.value.trim(),
        password: password.value,
      }),
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (err) {
            throw new Error(err.detail || 'Registration failed.');
          });
        }
        return res.json();
      })
      .then(function (data) {
        hideSpinner();

        showToast({
          type: 'success',
          title: 'Account created',
          message: 'You can now log in and explore the dashboard.',
        });

        setTimeout(function () {
          window.location.href = 'login.html';
        }, 900);
      })
      .catch(function (err) {
        hideSpinner();
        showToast({
          type: 'error',
          title: 'Registration failed',
          message: err.message || 'An error occurred. Please try again.',
        });
      });
  }

  document.addEventListener('DOMContentLoaded', function () {
    global.initCommonUI();
    handleRedirectToast();

    const loginForm = $('login-form');
    const registerForm = $('register-form');

    if (loginForm) {
      loginForm.addEventListener('submit', handleLoginSubmit);
    }

    if (registerForm) {
      registerForm.addEventListener('submit', handleRegisterSubmit);

      const password = $('regPassword');
      if (password) {
        password.addEventListener('input', function () {
          updatePasswordStrengthUI(password.value);
        });
      }
    }
  });
})();
