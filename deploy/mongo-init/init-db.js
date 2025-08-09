// MongoDB initialization script for local development

// Create the database
db = db.getSiblingDB('wardrobe_db');

// Create a user for the application
db.createUser({
    user: 'app_user',
    pwd: 'app_password',
    roles: [
        {
            role: 'readWrite',
            db: 'wardrobe_db'
        }
    ]
});

// Create collections with validation schemas
db.createCollection('clothing_items', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['category', 'colors', 'image_path'],
            properties: {
                category: {
                    bsonType: 'string',
                    enum: ['dress', 'shirt', 't-shirt', 'longsleeve', 'pants', 'shorts', 'skirt', 'shoes', 'hat', 'outwear', 'other']
                },
                colors: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'string'
                    }
                },
                image_path: {
                    bsonType: 'string'
                },
                created_at: {
                    bsonType: 'date'
                },
                updated_at: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// Create indexes for performance
db.clothing_items.createIndex({ category: 1 });
db.clothing_items.createIndex({ colors: 1 });
db.clothing_items.createIndex({ created_at: 1 });

// Create outfits collection
db.createCollection('outfits', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['name', 'items'],
            properties: {
                name: {
                    bsonType: 'string'
                },
                items: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'objectId'
                    }
                },
                created_at: {
                    bsonType: 'date'
                },
                updated_at: {
                    bsonType: 'date'
                }
            }
        }
    }
});

db.outfits.createIndex({ name: 1 });
db.outfits.createIndex({ created_at: 1 });

print('Database initialized successfully!');
