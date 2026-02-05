from bson.objectid import ObjectId




def get_campaign_with_latest_snapshot(run_id, campaigns_collection):
    _id = ObjectId(run_id)
    pipeline = [
        {"$match": {"_id": _id}},
        # Join with posts collection to get post details without unwinding
        {"$lookup": {
            "from": "posts",
            "localField": "posts",
            "foreignField": "_id",
            "as": "post_details"
        }},
        # Join with creator collection within each post in post_details array
        {"$lookup": {
            "from": "creators",
            "localField": "post_details.creator",
            "foreignField": "_id",
            "as": "creator_info"
        }},
        # Project specific fields, getting the last item in each snapshot array and maintaining array structure
        {"$project": {
            "name": 1,
            "status": 1,
            "post_details": {
                "$map": {
                    "input": "$post_details",
                    "as": "post",
                    "in": {
                        "_id":"$$post._id",
                        "platform": "$$post.platform",
                        "status":"$$post.status",
                        "link": "$$post.link",
                        "format": "$$post.format",
                        "postType": "$$post.postType",
                        "snapshot": {"$arrayElemAt": ["$$post.snapshot", -1]},
                        "tik_tok_snapshot": {"$arrayElemAt": ["$$post.tik_tok_snapshot", -1]},
                        "instagram_snapshot": {"$arrayElemAt": ["$$post.instagram_snapshot", -1]},
                        "video": "$$post.video",
                        "creator_info": {
                            "$arrayElemAt": [
                                {
                                    "$filter": {
                                        "input": "$creator_info",
                                        "as": "creator",
                                        "cond": {"$eq": ["$$creator._id", "$$post.creator"]}
                                    }
                                },
                                0
                            ]
                        }
                    }
                }
            }
        }}
    ]

    result = list(campaigns_collection.aggregate(pipeline))
    return result[0] if result else None  # Return single document if available
