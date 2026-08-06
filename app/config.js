// Filled in once the organiser creates the Supabase project (see app/sql/schema.sql).
// The anon key is safe to publish: security lives in the database rules — every
// table is deny-all and the key can only call the three game RPCs.
window.FEDORA_CONFIG = {
  SUPABASE_URL: "https://ntgsksywctywwzzaaffq.supabase.co",
  SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50Z3Nrc3l3Y3R5d3d6emFhZmZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU5Nzk3OTEsImV4cCI6MjEwMTU1NTc5MX0.JTiEkdlDgPx-DlFfKGUWRCAuHNaoi4Jx6uKEDUMBveE",
  HUNT_ID: "london-1",
};
