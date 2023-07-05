def all_customers(client, login_customer_id=None):
    """Gets the account hierarchy of the given MCC and login customer ID.

    Args:
      client: The Google Ads client.
      login_customer_id: Optional manager account ID. If none provided, this
      method will instead list the accounts accessible from the
      authenticated Google Ads account.
    """

    # Gets instances of the GoogleAdsService and CustomerService clients.
    googleads_service = client.get_service("GoogleAdsService")
    customer_service = client.get_service("CustomerService")


    # If a Manager ID was provided in the customerId parameter, it will be
    # the only ID in the list. Otherwise, we will issue a request for all
    # customers accessible by this authenticated Google account.
    seed_customer_ids = []
    if login_customer_id is None:
        customer_resource_names = (
            customer_service.list_accessible_customers().resource_names
        )
        for customer_resource_name in customer_resource_names:
            customer_id = googleads_service.parse_customer_path(
                customer_resource_name
            )["customer_id"]
            c_query = f"""
                SELECT
                customer.status, customer.manager
                FROM customer
                WHERE customer.id = '{customer_id}'
            """
            try:
                c_result = googleads_service.search(customer_id=str(customer_id), query=c_query)
            except:
                continue
            c_customer = list(c_result)[0].customer
            if c_customer.manager or c_customer.status != 2:
                continue
            seed_customer_ids.append(customer_id)
        return seed_customer_ids
    
    # Creates a query that retrieves all child accounts of the manager
    # specified in search calls below.
    query = """
        SELECT
          customer_client.client_customer,
          customer_client.level,
          customer_client.manager,
          customer_client.descriptive_name,
          customer_client.currency_code,
          customer_client.time_zone,
          customer_client.id
        FROM customer_client
        WHERE customer_client.level <= 1"""
    
    seed_customer_ids = [login_customer_id]
    customer_ids_to_child_accounts = dict()

    for seed_customer_id in seed_customer_ids:
        # Performs a breadth-first search to build a Dictionary that maps
        # managers to their child accounts (customerIdsToChildAccounts).
        unprocessed_customer_ids = [seed_customer_id]
        root_customer_client = None

        while unprocessed_customer_ids:
            customer_id = int(unprocessed_customer_ids.pop(0))
            response = googleads_service.search(
                customer_id=str(customer_id), query=query
            )

            # Iterates over all rows in all pages to get all customer
            # clients under the specified customer's hierarchy.
            for googleads_row in response:
                customer_client = googleads_row.customer_client

                # The customer client that with level 0 is the specified
                # customer.
                if customer_client.level == 0:
                    if root_customer_client is None:
                        root_customer_client = customer_client
                    continue

                # For all level-1 (direct child) accounts that are a
                # manager account, the above query will be run against them
                # to create a Dictionary of managers mapped to their child
                # accounts for printing the hierarchy afterwards.
                if customer_id not in customer_ids_to_child_accounts:
                    customer_ids_to_child_accounts[customer_id] = []

                customer_ids_to_child_accounts[customer_id].append(
                    customer_client
                )

                if customer_client.manager:
                    # A customer can be managed by multiple managers, so to
                    # prevent visiting the same customer many times, we
                    # need to check if it's already in the Dictionary.
                    if (
                        customer_client.id not in customer_ids_to_child_accounts
                        and customer_client.level == 1
                    ):
                        unprocessed_customer_ids.append(customer_client.id)
    all_customers = []
    for accounts in customer_ids_to_child_accounts.values():
        for account in accounts:
            if not account.manager:
                all_customers.append(str(account.id))
    return all_customers
