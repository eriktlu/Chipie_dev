def crash_game():
    crashObj = Crash.objects.latest('round_start_time')
    lastCrashObj = Crash.objects.filter(round_number=crashObj.round_number-1)[0]

    #Channels conf
    group_name = 'crash'
    channel_layer = channels.layers.get_channel_layer()

    if lastCrashObj.timer > 0:
       
        # Timer state
        oldTimer = lastCrashObj.timer
        newTimer = Decimal(str(oldTimer)) - Decimal('.1')

        # Frontend jaoks mängijate info
        bets = get_bets(False, None, newTimer)

        Crash.objects.filter(round_number=crashObj.round_number-1).update(timer=newTimer)
        
        # Andmed frontendi
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'testtimer',
                'timer': str(newTimer),
                'result': str(lastCrashObj.result),
                'game': 2,
                'bets': bets
            }
        )

    else:
        if crashObj.over == False:
            
            # mängu state
            oldState = crashObj.result_state
            newState = Decimal(str(oldState)) + decimal.Decimal('.01')

            # Frontend jaoks mängijate info
            bets = get_bets(True, newState, None)

            Crash.objects.filter(id=crashObj.id).update(result_state=newState)

            if newState >= crashObj.result:
                Crash.objects.filter(id=crashObj.id).update(over=True)

                # Eelmise mängu tulemused frontendi jaoks
                prev_results = get_previous_crash_results()

                # Kaotajate/võitjate salvestamine andmebaasi
                crashBets()

                # Uue roundi vastuse genereerimine
                crashOver()

                # Andmed frontendi
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'testtry',
                        'state': str(newState),
                        'game': 1,
                        'bets': bets,
                        'prev_results': prev_results
                    }
                )
                return

            # Andmed frontendi
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'testtry',
                    'state': str(newState),
                    'game': 0,
                    'bets': bets
                }
            )