import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '電力需要AI予測ダッシュボード',
  description: 'AI技術を活用した高精度な電力需要予測システム',
  keywords: ['電力需要予測', 'AI', '機械学習', 'LightGBM', 'Keras', 'PyCaret', 'RandomForest'],
  authors: [{ name: 'Power Demand Prediction Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#0a0a0a',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
      </head>
      <body>{children}</body>
    </html>
  );
}
