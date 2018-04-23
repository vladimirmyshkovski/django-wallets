from bitcoin import privkey_to_pubkey
from bitcoin import compress
from bitcoin import pubkey_to_address
from blockcypher.constants import COIN_SYMBOL_MAPPINGS
from blockcypher.utils import is_valid_coin_symbol
from blockcypher.api import create_unsigned_tx, verify_unsigned_tx, make_tx_signatures, broadcast_signed_transaction

import logging

logger = logging.getLogger(__name__)

def not_simple_spend(from_privkey, to_addresses, to_satoshis, change_address=None,
        privkey_is_compressed=True, min_confirmations=0, api_key=None, coin_symbol='btc'):
    '''
    Simple method to spend from one single-key address to another.
    Signature takes place locally (client-side) after unsigned transaction is verified.
    Returns the tx_hash of the newly broadcast tx.
    If no change_address specified, change will be sent back to sender address.
    Note that this violates the best practice.
    To sweep, set to_satoshis=-1
    Compressed public keys (and their corresponding addresses) have been the standard since v0.6,
    set privkey_is_compressed=False if using uncompressed addresses.
    Note that this currently only supports spending from single key addresses.
    '''
    assert is_valid_coin_symbol(coin_symbol), coin_symbol
    assert api_key, 'api_key required'
    assert type(to_addresses) and type(to_satoshis) is list
    assert len(to_addresses) == len(to_satoshis)
    for i in to_satoshis:
        assert type(i) is int, i


    if privkey_is_compressed:
        from_pubkey = compress(privkey_to_pubkey(from_privkey))
    else:
        from_pubkey = privkey_to_pubkey(from_privkey)
            
    from_address = pubkey_to_address(
            pubkey=from_pubkey,
            # this method only supports paying from pubkey anyway
            magicbyte=COIN_SYMBOL_MAPPINGS[coin_symbol]['vbyte_pubkey'],
            )

    inputs = [{'address': from_address}, ]
    logger.info('inputs: %s' % inputs)
    outputs = []
    for i in range(len(to_addresses)):
        outputs.append(
            {
                'address': to_addresses[i],
                'value': to_satoshis[i]
            }
        )

    #outputs = [{'address': to_address, 'value': to_satoshis}, ]
    logger.info('outputs: %s' % outputs)

    # will fail loudly if tx doesn't verify client-side
    unsigned_tx = create_unsigned_tx(
        inputs=inputs,
        outputs=outputs,
        # may build with no change address, but if so will verify change in next step
        # done for extra security in case of client-side bug in change address generation
        change_address=change_address,
        coin_symbol=coin_symbol,
        min_confirmations=min_confirmations,
        verify_tosigntx=False,  # will verify in next step
        include_tosigntx=True,
        api_key=api_key,
        )
    logger.info('unsigned_tx: %s' % unsigned_tx)

    if 'errors' in unsigned_tx:
        print('TX Error(s): Tx NOT Signed or Broadcast')
        for error in unsigned_tx['errors']:
            print(error['error'])
        # Abandon
        raise Exception('Build Unsigned TX Error')

    if change_address:
        change_address_to_use = change_address
    else:
        change_address_to_use = from_address

    tx_is_correct, err_msg = verify_unsigned_tx(
            unsigned_tx=unsigned_tx,
            inputs=inputs,
            outputs=outputs,
            sweep_funds=bool(to_satoshis == -1),
            change_address=change_address_to_use,
            coin_symbol=coin_symbol,
            )
    if not tx_is_correct:
        print(unsigned_tx)  # for debug
        raise Exception('TX Verification Error: %s' % err_msg)

    privkey_list, pubkey_list = [], []
    for proposed_input in unsigned_tx['tx']['inputs']:
        privkey_list.append(from_privkey)
        pubkey_list.append(from_pubkey)
        # paying from a single key should only mean one address per input:
        assert len(proposed_input['addresses']) == 1, proposed_input['addresses']
    # logger.info('privkey_list: %s' % privkey_list)
    logger.info('pubkey_list: %s' % pubkey_list)

    # sign locally
    tx_signatures = make_tx_signatures(
            txs_to_sign=unsigned_tx['tosign'],
            privkey_list=privkey_list,
            pubkey_list=pubkey_list,
            )
    logger.info('tx_signatures: %s' % tx_signatures)

    # broadcast TX
    broadcasted_tx = broadcast_signed_transaction(
            unsigned_tx=unsigned_tx,
            signatures=tx_signatures,
            pubkeys=pubkey_list,
            coin_symbol=coin_symbol,
            api_key=api_key,
    )
    logger.info('broadcasted_tx: %s' % broadcasted_tx)

    if 'errors' in broadcasted_tx:
        print('TX Error(s): Tx May NOT Have Been Broadcast')
        for error in broadcasted_tx['errors']:
            print(error['error'])
        print(broadcasted_tx)
        return

    return broadcasted_tx['tx']['hash']