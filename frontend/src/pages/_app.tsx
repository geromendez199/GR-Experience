import type { AppProps } from 'next/app';
import { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';

import Layout from '@/components/Layout';
import { createQueryClient } from '@/lib/queryClient';

import '@/styles/globals.css';

const App = ({ Component, pageProps }: AppProps) => {
  const [client] = useState(() => createQueryClient());
  return (
    <QueryClientProvider client={client}>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </QueryClientProvider>
  );
};

export default App;
