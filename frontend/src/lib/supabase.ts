import { createClient } from '@supabase/supabase-js';

// Ensure we have valid URLs for build time
const supabaseUrl =
  process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey =
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0';

// Validate required environment variables
if (
  !process.env.NEXT_PUBLIC_SUPABASE_URL &&
  process.env.NODE_ENV === 'production'
) {
  throw new Error(
    'Missing required environment variable: NEXT_PUBLIC_SUPABASE_URL'
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Auth helpers
export const signInWithGitHub = () => {
  return supabase.auth.signInWithOAuth({
    provider: 'github',
    options: {
      redirectTo: `${window.location.origin}/dashboard`,
    },
  });
};

export const signOut = () => {
  return supabase.auth.signOut();
};

export const getUser = () => {
  return supabase.auth.getUser();
};
