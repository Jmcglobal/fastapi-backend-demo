# Database Migration Guide

## ✅ Migration Created Successfully!

A migration file has been generated:
- **File**: `alembic/versions/4a6639b93e4a_initial_migration_users_and_contents_.py`
- **Revision ID**: `4a6639b93e4a`
- **Description**: Initial migration - users and contents tables

## 📋 What the Migration Creates

### Users Table
- `id` (Primary Key, Auto-increment)
- `name` (Indexed)
- `email` (Unique, Indexed)
- `phone_number` (Unique, Indexed)
- `country`
- `state`
- `created_at`

### Contents Table
- `id` (Primary Key, Auto-increment)
- `title` (Indexed)
- `image` (Optional)
- `content`
- `user_id` (Foreign Key → users.id, Indexed)
- `created_at`

### Indexes Created
✅ `ix_users_name` - Fast name lookups
✅ `ix_users_email` - Unique email, fast lookups
✅ `ix_users_phone_number` - Unique phone, fast lookups
✅ `ix_contents_title` - Fast title searches
✅ `ix_contents_user_id` - Fast user content queries

### Foreign Keys
✅ `contents.user_id` → `users.id`

## 🚀 How to Apply the Migration

### Step 1: Ensure Database Exists

```bash
# Check if database exists
psql -h localhost -U admin -d fastapi -c "SELECT 1;"

# If database doesn't exist, create it
createdb -h localhost -U admin fastapi

# Or using psql
psql -h localhost -U admin postgres
CREATE DATABASE fastapi;
\q
```

### Step 2: Apply the Migration

```bash
cd /Users/Jmcglobal/My-Files/Spenda/demo-git-action
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 4a6639b93e4a, Initial migration - users and contents tables
```

### Step 3: Verify Migration

```bash
# Check current migration version
alembic current

# Should show:
# 4a6639b93e4a (head)
```

### Step 4: Verify Tables Were Created

```bash
# Connect to database
psql -h localhost -U admin -d fastapi

# List tables
\dt

# Should show:
# users
# contents
# alembic_version

# Describe users table
\d users

# Describe contents table
\d contents

# Exit
\q
```

## 🔍 Migration Commands Reference

### Check Current Version
```bash
alembic current
```

### View Migration History
```bash
alembic history
```

### Upgrade to Latest
```bash
alembic upgrade head
```

### Downgrade One Version
```bash
alembic downgrade -1
```

### Downgrade to Specific Version
```bash
alembic downgrade 4a6639b93e4a
```

### Downgrade All (Remove All Tables)
```bash
alembic downgrade base
```

## 🔧 Troubleshooting

### Error: "Can't locate revision identified by '4a6639b93e4a'"

**Solution:**
The migration file exists. Just run:
```bash
alembic upgrade head
```

### Error: "FATAL: database 'fastapi' does not exist"

**Solution:**
Create the database first:
```bash
createdb -h localhost -U admin fastapi
# Then run migration
alembic upgrade head
```

### Error: "password authentication failed for user 'admin'"

**Solution:**
Check your `.env` file credentials:
```bash
cat .env
# Verify DB_URL is correct
# DB_URL=postgresql://admin:admin1234@localhost:5432/fastapi
```

### Error: "relation 'users' already exists"

**Solution:**
Tables already exist. Check current version:
```bash
alembic current
# If it shows nothing, stamp the database:
alembic stamp head
```

### Error: "Target database is not up to date"

**Solution:**
```bash
# View history
alembic history

# Upgrade to latest
alembic upgrade head
```

## 📝 Creating New Migrations

After modifying models in `src/models/`:

```bash
# 1. Generate new migration
alembic revision --autogenerate -m "Description of changes"

# 2. Review the generated file in alembic/versions/

# 3. Apply the migration
alembic upgrade head
```

## 🎯 Quick Start Checklist

- [ ] Database `fastapi` exists
- [ ] `.env` file configured with correct DB_URL
- [ ] PostgreSQL is running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Run `alembic upgrade head`
- [ ] Verify with `alembic current`

## 📊 Database Connection Details

Based on your `.env.example`:
```
Host: localhost
Port: 5432
Database: fastapi
Username: admin
Password: admin1234
```

## 🎉 Success Indicators

After running `alembic upgrade head`, you should see:

1. ✅ No errors in terminal
2. ✅ `alembic current` shows: `4a6639b93e4a (head)`
3. ✅ Tables visible in database: `users`, `contents`, `alembic_version`
4. ✅ Indexes created on all specified columns
5. ✅ Foreign key constraint on `contents.user_id`

## 🔄 Next Steps

After successful migration:

1. Start the FastAPI server:
   ```bash
   cd src
   python main.py
   ```

2. Test the API:
   ```bash
   # Health check
   curl http://localhost:8000/
   
   # Signup
   curl -X POST http://localhost:8000/api/v1/signup \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john@example.com",
       "phone_number": "+2348012345678",
       "country": "Nigeria",
       "state": "Lagos"
     }'
   ```

3. Access documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 💡 Pro Tips

1. **Always review auto-generated migrations** before applying them
2. **Test migrations in development** before production
3. **Backup your database** before running migrations in production
4. **Use descriptive migration messages** for easy tracking
5. **Version control your migration files** (they're already in the repo)

---

**Migration Status**: ✅ Ready to apply
**Command**: `alembic upgrade head`
