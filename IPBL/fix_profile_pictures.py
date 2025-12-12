"""
Script to check and fix profile picture paths in the database
"""
import os
from database import get_db

def fix_profile_pictures():
    db = get_db()
    
    # Get all users with profile pictures
    users = db.execute("""
        SELECT id, full_name, profile_picture 
        FROM users 
        WHERE profile_picture IS NOT NULL 
        AND profile_picture != 'default-avatar.png'
        AND profile_picture NOT LIKE 'https://ui-avatars.com%'
    """).fetchall()
    
    print(f"Found {len(users)} users with custom profile pictures\n")
    
    upload_dir = "static/uploads/profile_pics"
    available_files = set(os.listdir(upload_dir)) if os.path.exists(upload_dir) else set()
    
    print(f"Available files in {upload_dir}:")
    for f in sorted(available_files):
        print(f"  - {f}")
    print()
    
    issues_found = []
    
    for user in users:
        user_id = user['id']
        full_name = user['full_name']
        profile_pic = user['profile_picture']
        
        print(f"User #{user_id} ({full_name}):")
        print(f"  Database path: {profile_pic}")
        
        # Extract filename from path
        if profile_pic.startswith('/'):
            filename = profile_pic.split('/')[-1]
        else:
            filename = profile_pic
        
        # Check if file exists
        file_path = os.path.join(upload_dir, filename)
        exists = os.path.exists(file_path)
        
        print(f"  Filename: {filename}")
        print(f"  File exists: {exists}")
        
        if not exists:
            # Try to find a similar file
            # Look for files with similar patterns
            potential_matches = []
            
            # Extract the date pattern if present
            if '251201' in filename or '094917' in filename:
                for available_file in available_files:
                    if '251201_094917' in available_file or 'IMG_20251201_094917' in available_file:
                        potential_matches.append(available_file)
            
            if potential_matches:
                print(f"  Potential matches found:")
                for match in potential_matches:
                    print(f"    - {match}")
                
                # Use the first match
                correct_filename = potential_matches[0]
                correct_path = f"/{upload_dir}/{correct_filename}"
                
                print(f"  Suggested fix: Update to {correct_path}")
                issues_found.append({
                    'user_id': user_id,
                    'full_name': full_name,
                    'old_path': profile_pic,
                    'new_path': correct_path
                })
            else:
                print(f"  ⚠️ No matching file found!")
                issues_found.append({
                    'user_id': user_id,
                    'full_name': full_name,
                    'old_path': profile_pic,
                    'new_path': None
                })
        else:
            print(f"  ✓ File exists")
        
        print()
    
    if issues_found:
        print(f"\n{'='*60}")
        print(f"Found {len(issues_found)} issues:")
        print(f"{'='*60}\n")
        
        for issue in issues_found:
            print(f"User #{issue['user_id']} ({issue['full_name']}):")
            print(f"  Old: {issue['old_path']}")
            print(f"  New: {issue['new_path']}")
            
            if issue['new_path']:
                # Ask for confirmation
                response = input(f"  Fix this? (y/n): ").strip().lower()
                if response == 'y':
                    db.execute(
                        "UPDATE users SET profile_picture = %s WHERE id = %s",
                        (issue['new_path'], issue['user_id'])
                    )
                    db.commit()
                    print(f"  ✓ Updated!")
            else:
                print(f"  ⚠️ No fix available - consider setting to default")
            print()
    else:
        print("No issues found! All profile pictures are valid.")

if __name__ == "__main__":
    fix_profile_pictures()
