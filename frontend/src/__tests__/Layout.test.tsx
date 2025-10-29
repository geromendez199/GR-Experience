import { render, screen } from '@testing-library/react';

import Layout from '@/components/Layout';

const Dummy = () => <div>content</div>;

describe('Layout', () => {
  it('renders navigation links', () => {
    render(
      <Layout>
        <Dummy />
      </Layout>
    );
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Sessions')).toBeInTheDocument();
    expect(screen.getByText('Training')).toBeInTheDocument();
  });
});
