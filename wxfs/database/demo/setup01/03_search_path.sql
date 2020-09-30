ALTER ROLE wxfs IN DATABASE wxfs SET search_path = wxfs, public;
ALTER ROLE wxfs_rw IN DATABASE wxfs SET search_path = wxfs, public;
ALTER ROLE wxfs_ro IN DATABASE wxfs SET search_path = wxfs, public;