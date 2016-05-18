from app import db, models

evey = models.User(name="Evey AI",
                   profile_pic_id="",
                   synced_fb=1,
                   first_name='Evey'
                   last_name='AI'
                   email='')
db.session.add(evey)
db.session.commit()
