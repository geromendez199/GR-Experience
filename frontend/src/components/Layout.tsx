import Link from 'next/link';
import { useRouter } from 'next/router';
import { ReactNode } from 'react';

import styles from './Layout.module.css';

interface LayoutProps {
  children: ReactNode;
}

const navLinks = [
  { href: '/', label: 'Overview' },
  { href: '/sessions', label: 'Sessions' },
  { href: '/training', label: 'Training' },
  { href: '/replay', label: 'Replay 3D' }
];

const Layout = ({ children }: LayoutProps) => {
  const router = useRouter();

  return (
    <div className={styles.container}>
      <aside className={styles.sidebar}>
        <h1 className={styles.logo}>GR-Experience</h1>
        <nav>
          <ul>
            {navLinks.map((link) => (
              <li key={link.href} className={router.pathname === link.href ? styles.active : ''}>
                <Link href={link.href}>{link.label}</Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
      <main className={styles.main}>{children}</main>
    </div>
  );
};

export default Layout;
