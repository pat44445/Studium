<?php

namespace App\Model;

use DateTime;

class Utils
{
    public static function dateStringToObject(string $date): ?DateTime
    {
        $datetime = DateTime::createFromFormat('Y-m-d', $date);

        if (!$datetime) {
            return null;
        }

        return $datetime;
    }
}