// Filled in once the organiser creates the Supabase project (see app/sql/schema.sql).
// The anon key is safe to publish: security lives in the database rules — every
// table is deny-all and the key can only call the three game RPCs.
window.FEDORA_CONFIG = {
  SUPABASE_URL: "",
  SUPABASE_ANON_KEY: "",
  HUNT_ID: "london-1",
};
