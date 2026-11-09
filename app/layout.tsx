import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {title:'AJ133 | Diagnostic Explorer',description:'Schematic external oil leak investigation workspace'};
export default function Layout({children}:{children:React.ReactNode}) {return <html lang="en"><body>{children}</body></html>}
