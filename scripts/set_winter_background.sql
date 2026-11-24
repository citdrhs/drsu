-- Apply once when deploying the holiday background. Later image uploads remain editable.
UPDATE events
SET file_name = 'WinterGatheringHoliday.png'
WHERE LOWER(TRIM(name)) = 'winter gathering';
