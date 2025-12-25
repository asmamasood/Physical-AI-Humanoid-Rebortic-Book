import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import { useSession, signOut } from '../lib/auth-client';
import { useHistory } from '@docusaurus/router';
import axios from 'axios';
import styles from './profile.module.css';

const SOFTWARE_ROLES = ['Frontend', 'Backend', 'AI/ML', 'Fullstack', 'DevOps', 'Other'];
const SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced'];
const HARDWARE_TYPES = ['Low-end PC', 'Mid-range PC', 'High-end PC', 'Mobile-only'];

export default function ProfilePage() {
    const { data: session, isPending } = useSession();
    const history = useHistory();
    const [profile, setProfile] = useState<any>(null);
    const [leaderboard, setLeaderboard] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [softwareRole, setSoftwareRole] = useState('');
    const [softwareLevel, setSoftwareLevel] = useState('');
    const [hardwareType, setHardwareType] = useState('');
    const [gpuAvailable, setGpuAvailable] = useState(false);
    const [preferredLanguage, setPreferredLanguage] = useState('en');
    const [agentName, setAgentName] = useState('');
    const [agentPersona, setAgentPersona] = useState('');
    const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
    const [creatingAgent, setCreatingAgent] = useState(false);
    const [agents, setAgents] = useState<any[]>([]);
    const [skills, setSkills] = useState<any[]>([]);
    
    useEffect(() => {
        if (session?.user?.id) {
            const userId = session.user.id;
            fetchProfile(userId);
            fetchLeaderboard();
            fetchAgents(userId);
            fetchSkills();
        }
    }, [session]);

    const fetchProfile = async (userId: string) => {
        try {
            const res = await axios.get(`http://localhost:8000/api/profile/full/${userId}`);
            setProfile(res.data);
            if (res.data.background) {
                setSoftwareRole(res.data.background.software_role || '');
                setSoftwareLevel(res.data.background.software_level || '');
                setHardwareType(res.data.background.hardware_type || '');
                setGpuAvailable(res.data.background.gpu_available || false);
            }
        } catch (err) {
            console.error("Fetch profile failed:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchLeaderboard = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/leaderboard');
            setLeaderboard(res.data.top_users || []);
        } catch (err) {
            console.error("Fetch leaderboard failed:", err);
        }
    };

    const fetchAgents = async (userId: string) => {
        try {
            const res = await axios.get(`http://localhost:8000/api/agents/${userId}`);
            setAgents(res.data || []);
        } catch (err) {
            console.error("Fetch agents failed:", err);
        }
    };

    const fetchSkills = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/skills');
            setSkills(res.data || []);
        } catch (err) {
            console.error("Fetch skills failed:", err);
        }
    };

    const handleSignOut = async () => {
        try {
            console.log("Signing out...");
            await signOut();
            console.log("Sign out successful, redirecting...");
            history.push('/');
        } catch (err) {
            console.error("Sign out failed:", err);
            // Even if it fails on server, we should probably try to redirect or clear state
            history.push('/');
        }
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setError('');
        setMessage('');
        try {
            await axios.post('http://localhost:8000/api/profile', {
                user_id: session.user.id,
                software_role: softwareRole,
                software_level: softwareLevel,
                hardware_type: hardwareType,
                gpu_available: gpuAvailable
            });
            setMessage('Settings saved successfully!');
            fetchProfile(session.user.id);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save settings');
        } finally {
            setSaving(false);
        }
    };

    const handleCreateAgent = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreatingAgent(true);
        setError('');
        try {
            await axios.post('http://localhost:8000/api/agents', {
                user_id: session.user.id,
                name: agentName,
                persona: agentPersona,
                skills: selectedSkills
            });
            setAgentName('');
            setAgentPersona('');
            setSelectedSkills([]);
            fetchAgents(session.user.id);
            fetchProfile(session.user.id); // Refresh points
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create agent');
        } finally {
            setCreatingAgent(false);
        }
    };

    if (isPending || loading) {
        return (
            <Layout title="Your Profile">
                <div className={styles.loading}>Loading your profile...</div>
            </Layout>
        );
    }

    return (
        <Layout title="Your Profile">
            <div className={styles.container}>
                <div className={styles.header}>
                    <h1>Welcome, {session.user.name}</h1>
                    <p>{session.user.email}</p>
                    <div className={styles.buttonGroup}>
                        <button 
                            onClick={() => history.push('/docs/intro')}
                            className={styles.backButton}
                        >
                            ← Back to Textbook
                        </button>
                        <button 
                            onClick={handleSignOut}
                            className={styles.signOutButton}
                            style={{marginLeft: '10px', backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer'}}
                        >
                            Sign Out
                        </button>
                    </div>
                </div>

                <div className={styles.grid}>
                    {/* Gamification Stats */}
                    <div className={styles.card}>
                        <h2>🏆 Learning Progress</h2>
                        <div className={styles.stats}>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Level</span>
                                <span className={styles.statValue}>{profile?.status?.level || 1}</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Total Points</span>
                                <span className={styles.statValue}>{profile?.status?.points_total || 0}</span>
                            </div>
                        </div>
                        <div className={styles.progressBar}>
                            <div 
                                className={styles.progressFill} 
                                style={{ width: `${(profile?.status?.points_total % 100)}%` }}
                            />
                        </div>
                        <p className={styles.hint}>Earn points by interacting with the chatbot and completing chapters!</p>
                    </div>

                    {/* Leaderboard Card */}
                    <div className={styles.card}>
                        <h2>🔥 Global Leaderboard</h2>
                        <div className={styles.leaderboard}>
                            {leaderboard.map((entry, index) => (
                                <div key={entry.user_id} className={`${styles.lbEntry} ${entry.user_id === session.user.id ? styles.lbMe : ''}`}>
                                    <span className={styles.lbRank}>{index + 1}</span>
                                    <span className={styles.lbUser}>{entry.user_id === session.user.id ? 'You' : `User ${entry.user_id.substring(0, 5)}...`}</span>
                                    <span className={styles.lbPoints}>{entry.points_total} pts</span>
                                    <span className={styles.lbLevel}>Lvl {entry.level}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Personalization Settings */}
                    <div className={styles.card}>
                        <h2>⚙️ Personalization Settings</h2>
                        {/* ... form content same as before ... */}
                        <form onSubmit={handleSave}>
                            {/* ... fields ... */}
                            <div className={styles.field}>
                                <label>Software Role</label>
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
                                    I have a GPU available
                                </label>
                            </div>
                            <div className={styles.field}>
                                <label>Preferred Language</label>
                                <select value={preferredLanguage} onChange={(e) => setPreferredLanguage(e.target.value)}>
                                    <option value="en">English</option>
                                    <option value="ur">Urdu (اردو)</option>
                                </select>
                            </div>
                            
                            {error && !agentName && <p className={styles.error}>{error}</p>}
                            {message && <p className={styles.success}>{message}</p>}

                            <button type="submit" className={styles.saveButton} disabled={saving}>
                                {saving ? 'Saving...' : 'Save Settings'}
                            </button>
                        </form>
                    </div>

                    {/* AI Subagents Studio */}
                    <div className={`${styles.card} ${styles.fullWidth}`}>
                        <h2>🤖 AI Subagent Studio</h2>
                        <div className={styles.studioGrid}>
                            {/* Agent Creator */}
                            <div className={styles.creatorForm}>
                                <h3>Create New Persona</h3>
                                <form onSubmit={handleCreateAgent}>
                                    <div className={styles.field}>
                                        <label>Agent Name</label>
                                        <input 
                                            type="text" 
                                            placeholder="e.g. Matrix Mentor" 
                                            value={agentName}
                                            onChange={(e) => setAgentName(e.target.value)}
                                            required
                                        />
                                    </div>
                                    <div className={styles.field}>
                                        <label>Persona Description</label>
                                        <textarea 
                                            placeholder="How should this agent behave? (e.g. Strict but helpful coding coach)"
                                            value={agentPersona}
                                            onChange={(e) => setAgentPersona(e.target.value)}
                                            required
                                            rows={3}
                                            style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                                        />
                                    </div>
                                    <div className={styles.field}>
                                        <label>Equip Skills</label>
                                        <div className={styles.skillsSelect}>
                                            {skills.map(skill => (
                                                <label key={skill.id} className={styles.skillEntry}>
                                                    <input 
                                                        type="checkbox"
                                                        checked={selectedSkills.includes(skill.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) setSelectedSkills([...selectedSkills, skill.id]);
                                                            else setSelectedSkills(selectedSkills.filter(id => id !== skill.id));
                                                        }}
                                                    />
                                                    <span>{skill.name}</span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>
                                    <button type="submit" className={styles.saveButton} disabled={creatingAgent}>
                                        {creatingAgent ? 'Creating AI...' : 'Forge Subagent (+50 pts)'}
                                    </button>
                                </form>
                            </div>

                            {/* My Agents List */}
                            <div className={styles.agentsList}>
                                <h3>My Active Personas</h3>
                                {agents.length === 0 ? (
                                    <p className={styles.hint}>No subagents created yet. Build your first AI assistant!</p>
                                ) : (
                                    <div className={styles.agentGrid}>
                                        {agents.map(agent => (
                                            <div key={agent.id} className={styles.agentCard}>
                                                <div className={styles.agentAvatar}>🤖</div>
                                                <div className={styles.agentInfo}>
                                                    <h4>{agent.name}</h4>
                                                    <p>{agent.persona_description}</p>
                                                    <div className={styles.agentSkills}>
                                                        {agent.skill_ids.map(sid => {
                                                            const skill = skills.find(s => s.id === sid);
                                                            return skill ? <span key={sid} className={styles.skillTag}>{skill.name}</span> : null;
                                                        })}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
}
