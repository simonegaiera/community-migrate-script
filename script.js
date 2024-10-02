db.getMongo().getDBNames().forEach(
    function (d)
       {
         print("Database: " + d );
         var curr_db = db.getSiblingDB(d);
         printjson( curr_db.stats());
       }
    );