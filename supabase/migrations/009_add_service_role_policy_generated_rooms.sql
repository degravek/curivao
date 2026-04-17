-- Restore the service_role policy that Supabase auto-creates on dashboard-created tables.
-- Migration 008 dropped and recreated generated_rooms via SQL, losing the auto-policy.

create policy "Allow service role full access"
  on generated_rooms
  for all
  to service_role
  using (true)
  with check (true);
