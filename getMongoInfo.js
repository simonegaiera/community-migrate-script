// collect everything here
var out = [];

db.getMongo().getDBNames().forEach(function (d) {
  var curr_db = db.getSiblingDB(d);

  // get raw stats
  out.push( curr_db.stats() );

  curr_db.getCollectionInfos({ type: "collection" }).forEach(function (info) {
    out.push( curr_db.getCollection(info.name).stats() );
  });
});

// print ONE valid JSON array
print(EJSON.stringify(out, { relaxed: false }));