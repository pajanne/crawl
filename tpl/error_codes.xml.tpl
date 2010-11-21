<response>
    <results name=$response.name>
    #for $error_code in $response.error_codes:
        <code code=$error_code.code type=$error_code.type />
    #end for
    </results>
</response>
