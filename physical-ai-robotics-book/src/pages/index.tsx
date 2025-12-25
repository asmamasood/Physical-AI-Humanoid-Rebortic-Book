import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

import { useSession } from '../lib/auth-client';
import { useHistory } from '@docusaurus/router';

function HeroSection() {
  const {siteConfig} = useDocusaurusContext();
  const { data: session } = useSession();
  
  const scrollToContent = () => {
    const content = document.getElementById('features');
    content?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <header className={styles.heroBanner}>
      <div className={styles.heroBackground} />
      <div className={styles.container}>
        {/* Left Side: Text */}
        <div className={styles.heroContent}>
          <Heading as="h1" className={styles.title}>
            Physical AI &<br />Humanoid Robotics
          </Heading>
          <p className={styles.subtitle}>
            A definitive guide to <strong>Embodied Intelligence</strong>. 
            Bridging the gap between digital algorithms and physical reality for the next generation of robotics.
          </p>
          <div className={styles.buttons}>
            <Link
              className="button button--primary button--lg"
              to={session ? "/docs/intro" : "/login"}>
              {session ? "Start Reading" : "Get Started"}
            </Link>
            <Link
              className="button button--secondary button--lg"
              to="/docs/intro">
              View Curriculum
            </Link>
          </div>
        </div>

        {/* Right Side: Hero Image */}
        <div className={styles.heroImageWrapper}>
          <img 
            src="img/hero-light.png" 
            alt="Physical AI Connection" 
            className={styles.heroImage}
          />
        </div>
      </div>
      
      <div className={styles.scrollDown} onClick={scrollToContent}>
        ↓
      </div>
    </header>
  );
}

const FeatureList = [
  {
    title: 'Embodied Intelligence',
    icon: '🤖',
    tags: ['Cognition', 'Sensors'],
    description: (
      <>
        Understand how physical bodies influence cognition.
        Dive deep into sensorimotor loops and the physics of interaction.
      </>
    ),
  },
  {
    title: 'Advanced Control',
    icon: '🎮',
    tags: ['PID', 'LQR', 'MPPI'],
    description: (
      <>
        Master classical and modern control theory. Implement stable walking
        gaits and robust manipulation strategies on real hardware.
      </>
    ),
  },
  {
    title: 'Computer Vision',
    icon: '👁️',
    tags: ['SLAM', 'Depth', 'YOLO'],
    description: (
      <>
        Give your robot the ability to perceive its world. Implement
        SLAM, object detection, and depth estimation pipelines.
      </>
    ),
  },
  {
    title: 'Simulation & Sim2Real',
    icon: '🖥️',
    tags: ['MuJoCo', 'Isaac Gym'],
    description: (
      <>
        Train policies in high-fidelity simulation and transfer them
        zero-shot to physical robots using domain randomization.
      </>
    ),
  },
  {
    title: 'Reinforcement Learning',
    icon: '🧠',
    tags: ['PPO', 'SAC'],
    description: (
      <>
        Train neural networks to solve complex motor control tasks
        from scratch using Deep Reinforcement Learning.
      </>
    ),
  },
  {
    title: 'Humanoid Locomotion',
    icon: '🚶',
    tags: ['ZMP', 'WBC'],
    description: (
      <>
        Specialized module on bipedal walking dynamics, Zero Moment Point,
        and Whole-Body Control strategies for humanoids.
      </>
    ),
  },
];

function FeaturesSection() {
  return (
    <section id="features" className={styles.features}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>Curriculum Overview</h2>
        <div className={styles.featureGrid}>
          {FeatureList.map((props, idx) => (
            <div key={idx} className={styles.featureCard}>
              <div className={styles.featureIcon}>{props.icon}</div>
              <h3 className={styles.featureTitle}>{props.title}</h3>
              <p className={styles.featureDesc}>{props.description}</p>
              <div className={styles.tags}>
                {props.tags.map((tag, tIdx) => (
                  <span key={tIdx} className={styles.tag}>{tag}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}


export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const { data: session } = useSession();

  return (
    <Layout
      title={`${siteConfig.title}`}
      description="A comprehensive guide to Physical AI and Humanoid Robotics.">
      <main>
        <HeroSection />
        <FeaturesSection />
      </main>
    </Layout>
  );
}
