import React, { useState } from 'react';
import Layout from '@theme/Layout';
import { signUp } from '../lib/auth-client';
import { useHistory } from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './auth.module.css';
import clsx from 'clsx';

const SOFTWARE_ROLES = ['Frontend', 'Backend', 'AI/ML', 'Fullstack', 'DevOps', 'Other'];
const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced'];
const HARDWARE_TYPES = ['Low-end PC', 'Mid-range PC', 'High-end PC', 'Mobile-only'];

function SignupPage() {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [softwareRole, setSoftwareRole] = useState('');
  const [softwareLevel, setSoftwareLevel] = useState('');
  const [hardwareType, setHardwareType] = useState('');
  const [gpuAvailable, setGpuAvailable] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const history = useHistory();
  const homeUrl = useBaseUrl('/'); 

  const handleStep1 = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await signUp.email({ name, email, password });
      // @ts-ignore - Handle dynamic response structure from Better Auth
      const user = result?.data?.user || result?.user || result?.data;
      const id = user?.id;
      
      if (id) {
        setUserId(id);
        setStep(2);
      } else {
        setUserId(email);
        setStep(2);
      }
    } catch (err: any) {
      setError(err?.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStep2 = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await fetch('http://localhost:8000/api/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          software_role: softwareRole,
          software_level: softwareLevel,
          hardware_type: hardwareType,
          gpu_available: gpuAvailable
        })
      });
      history.push(homeUrl);
    } catch (err: any) {
      setError('Failed to save profile. You can update it later.');
      history.push(homeUrl);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Sign Up">
      <div className={styles.container}>
        <div className={styles.card}>
          <h1 className={styles.title}>{step === 1 ? 'Create Account' : 'Personalize Interface'}</h1>
          
          <div className={styles.stepIndicator}>
            <div className={clsx(styles.stepDot, step === 1 && styles.stepDotActive)} />
            <div className={clsx(styles.stepDot, step === 2 && styles.stepDotActive)} />
          </div>

          {error && <div className={styles.error}>{error}</div>}

          {step === 1 && (
            <form onSubmit={handleStep1}>
              <div className={styles.field}>
                <label htmlFor="name">Full Name</label>
                <input id="name" type="text" placeholder="John Doe" value={name} onChange={(e) => setName(e.target.value)} required />
              </div>
              <div className={styles.field}>
                <label htmlFor="email">Email Address</label>
                <input id="email" type="email" placeholder="john@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div className={styles.field}>
                <label htmlFor="password">Password</label>
                <input id="password" type="password" placeholder="At least 8 characters" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
              </div>
              <button type="submit" disabled={loading} className={styles.button}>
                {loading ? 'Creating Account...' : 'Continue →'}
              </button>
            </form>
          )}

          {step === 2 && (
            <form onSubmit={handleStep2}>
              <div className={styles.field}>
                <label>What is your software role?</label>
                <select value={softwareRole} onChange={(e) => setSoftwareRole(e.target.value)} required>
                  <option value="">Select role...</option>
                  {SOFTWARE_ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div className={styles.field}>
                <label>Experience Level</label>
                <select value={softwareLevel} onChange={(e) => setSoftwareLevel(e.target.value)} required>
                  <option value="">Select level...</option>
                  {SKILL_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
              </div>
              <div className={styles.field}>
                <label>Hardware Setup</label>
                <select value={hardwareType} onChange={(e) => setHardwareType(e.target.value)} required>
                  <option value="">Select hardware...</option>
                  {HARDWARE_TYPES.map(h => <option key={h} value={h}>{h}</option>)}
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.checkbox}>
                  <input type="checkbox" checked={gpuAvailable} onChange={(e) => setGpuAvailable(e.target.checked)} />
                  Dedicated GPU Available
                </label>
              </div>
              <button type="submit" disabled={loading} className={styles.button}>
                {loading ? 'Finalizing...' : 'Complete Registration'}
              </button>
              <button type="button" onClick={() => history.push(homeUrl)} style={{ width: '100%', marginTop: '10px', background: 'transparent', color: '#64748b', border: 'none', cursor: 'pointer', fontSize: '0.9rem' }}>
                Skip for now
              </button>
            </form>
          )}

          {step === 1 && (
            <p className={styles.footer}>
              Already have an account? <a href="/login">Sign In</a>
            </p>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default SignupPage;

