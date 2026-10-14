-- Run this ONCE against your existing `apartmentRental` database.
-- It adds floor and bedroom-type tracking to the APARTMENT table
-- without touching any existing rows, blocks, tenants or payments.

USE `apartmentRental`;

ALTER TABLE APARTMENT
    ADD COLUMN FLOOR_NO INTEGER AFTER BLOCK_NO,
    ADD COLUMN BEDROOM_TYPE VARCHAR(20) AFTER FLOOR_NO;

-- Optional: backfill FLOOR_NO for any rooms you already added, using the
-- convention ROOM_NO = <floor><unit>, e.g. 101 -> floor 1, 205 -> floor 2.
-- Adjust or skip this if your existing room numbers don't follow that pattern.
-- UPDATE APARTMENT SET FLOOR_NO = FLOOR(ROOM_NO / 100) WHERE FLOOR_NO IS NULL;

-- Optional: give existing rows a default bedroom type so old data still
-- shows up in the new filters until you edit each unit properly.
-- UPDATE APARTMENT SET BEDROOM_TYPE = '1 Bedroom' WHERE BEDROOM_TYPE IS NULL;
