db.createUser(
    {
        user: 'user',
        pwd: 'Pwd_SH0U1D_NO7_bE_Too_W33k',
        roles: [
            {
                role: 'readWrite',
                db: 'fuzz'
            }
        ]
    }
)

db.createCollection('request')
db.request.createIndex({ token: 1 }, { unique: true })

db.createCollection('response')
db.response.createIndex({ token: 1 }, { unique: true })

db.createCollection('diff')