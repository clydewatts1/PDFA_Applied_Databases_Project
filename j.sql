# I want a query of all space on a teradata system
SELECT Databasename,SUM(CurrentPerm) AS TotalSpace
FROM DBC.DISKSPACE
GROUP BY Databasename;
