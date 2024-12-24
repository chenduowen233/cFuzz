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
db.request.createIndex({ X_Token: 1 }, { unique: true })

db.createCollection('response')
db.response.createIndex({ X_Token: 1 }, { unique: true })

db.createCollection('diff')
